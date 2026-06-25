import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.db.models import Q

from .models import (
    AIInteraction,
    AISettings,
    BlogPost,
    CareerTrack,
    Certificate,
    CloudPost,
    ContactMessage,
    CyberFinding,
    Profile,
    Project,
    PythonPost,
    Resume,
    Skill,
    Video,
)


class AIResponse:
    def __init__(self, text, provider="local", model="", success=True, error=""):
        self.text = text
        self.provider = provider
        self.model = model
        self.success = success
        self.error = error


def get_ai_settings():
    settings = AISettings.objects.order_by("-updated_at").first()
    if settings:
        return settings
    return AISettings.objects.create()


def _request_json(url, payload, headers, timeout=25):
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _research_with_tavily(query):
    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        return []
    data = _request_json(
        "https://api.tavily.com/search",
        {"api_key": api_key, "query": query, "search_depth": "basic", "max_results": 5},
        {"Content-Type": "application/json"},
        timeout=20,
    )
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
        }
        for item in data.get("results", [])
    ]


def _research_with_serper(query):
    api_key = os.environ.get("SERPER_API_KEY", "").strip()
    if not api_key:
        return []
    data = _request_json(
        "https://google.serper.dev/search",
        {"q": query, "num": 5},
        {"Content-Type": "application/json", "X-API-KEY": api_key},
        timeout=20,
    )
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        }
        for item in data.get("organic", [])
    ]


def internet_research_context(query):
    if not query:
        return "Internet Research: No query provided."
    errors = []
    results = []
    for researcher in (_research_with_tavily, _research_with_serper):
        try:
            results = researcher(query)
            if results:
                break
        except (HTTPError, URLError, TimeoutError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    if not results:
        if errors:
            return "Internet Research: Search provider failed. " + " | ".join(errors[:2])
        return "Internet Research: No search API key configured. Add TAVILY_API_KEY or SERPER_API_KEY to enable live web research."
    lines = ["Internet Research:"]
    for index, item in enumerate(results, 1):
        lines.append(f"{index}. {item['title']} - {item['url']}\n   {item['snippet']}")
    return "\n".join(lines)


def extract_blog_fields(text):
    def section(name, next_names):
        pattern = rf"{re.escape(name)}:\s*(.*?)(?=\n(?:{'|'.join(re.escape(item) for item in next_names)}):|\Z)"
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    title = section("Blog Title", ["Short Excerpt", "Full Blog Draft", "SEO Title Ideas", "Suggested Tags"])
    excerpt = section("Short Excerpt", ["Full Blog Draft", "SEO Title Ideas", "Suggested Tags"])
    full_content = section("Full Blog Draft", ["SEO Title Ideas", "Suggested Tags", "Admin Notes Used", "Site Context Used"])
    seo_titles = section("SEO Title Ideas", ["Suggested Tags", "Admin Notes Used", "Site Context Used"])
    tags = section("Suggested Tags", ["Admin Notes Used", "Site Context Used"])
    if not title:
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "AI Generated Blog")
        title = first_line.replace("Blog Title:", "").strip()
    if not excerpt:
        excerpt = "AI-generated blog draft for TIPKODES TECH LAB."
    if not full_content:
        full_content = text
    return {
        "title": title[:220],
        "short_excerpt": excerpt[:320],
        "full_content": full_content.strip(),
        "ai_summary": excerpt[:1000],
        "ai_key_takeaways": "\n".join(line.strip("- ").strip() for line in full_content.splitlines() if line.strip().startswith("- "))[:1500],
        "seo_title": (seo_titles.splitlines()[0].strip("- ").strip() if seo_titles else title)[:180],
        "meta_description": excerpt[:320],
        "tags": [tag.strip() for tag in tags.replace("\n", ",").split(",") if tag.strip()][:8],
    }


def _call_groq(messages, settings):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    model = os.environ.get("GROQ_MODEL", settings.groq_model).strip() or settings.groq_model
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.35,
        "max_tokens": 900,
    }
    data = _request_json(
        "https://api.groq.com/openai/v1/chat/completions",
        payload,
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    return AIResponse(data["choices"][0]["message"]["content"].strip(), "groq", model)


def _call_gemini(messages, settings):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    model = os.environ.get("GEMINI_MODEL", settings.gemini_model).strip() or settings.gemini_model
    prompt = "\n\n".join(f"{item['role'].upper()}:\n{item['content']}" for item in messages)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {"temperature": 0.35, "maxOutputTokens": 900},
    }
    data = _request_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        payload,
        {"Content-Type": "application/json"},
    )
    parts = data["candidates"][0]["content"]["parts"]
    return AIResponse("".join(part.get("text", "") for part in parts).strip(), "gemini", model)


def _clean_blog_topic(notes):
    topic = " ".join((notes or "").strip().split())
    lowered = topic.lower()
    prefixes = [
        "write a blog post about ",
        "write blog post about ",
        "draft a blog post about ",
        "draft blog post about ",
        "create a blog post about ",
        "blog post about ",
        "write about ",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            topic = topic[len(prefix):].strip()
            break
    return topic.strip(" .") or "how I built TIPKODES TECH LAB"


def _local_blog_draft(notes, context):
    topic = _clean_blog_topic(notes)
    title = topic[0].upper() + topic[1:] if topic else "How I Built TIPKODES TECH LAB"
    title_lower = title.lower()
    project_context = "\n".join(line for line in context.splitlines() if line.startswith(("Profile:", "Project:", "Cloud:", "Skill:", "Resume summary:")))[:1200]
    research_context = "\n".join(line for line in context.splitlines() if line.startswith(("Internet Research:", "1.", "2.", "3.", "4.", "5.", "   ")))[:1500]
    research_note = research_context or "Internet Research: No live research results were available. Add TAVILY_API_KEY or SERPER_API_KEY, plus Groq/Gemini keys, for fresher researched writing."
    return (
        f"Blog Title: {title}\n\n"
        "Short Excerpt:\n"
        f"A professional guide to {title_lower}, written for learners, developers, and collaborators who want practical context, implementation lessons, and clear takeaways.\n\n"
        "Full Blog Draft:\n"
        f"{title}\n\n"
        "Introduction\n"
        f"{title} is an important topic because it connects practical learning with real implementation decisions. A strong technical blog should not only describe what was done; it should explain why it matters, what choices were made, what challenges appeared, and what other learners can take from the experience.\n\n"
        "Background\n"
        f"The main idea behind this topic is: {topic}. In a real-world project or learning environment, this means looking at the tools, workflow, design decisions, deployment process, security considerations, and long-term maintainability of the solution.\n\n"
        "Why This Matters\n"
        "Professional technical work is judged by more than whether it runs. It should be understandable, reliable, maintainable, and useful to its intended users. Documenting the process also helps others learn from the decisions and avoid repeating common mistakes.\n\n"
        "Implementation Approach\n"
        "A good implementation starts by defining the problem clearly. After that, the developer chooses the tools that fit the use case, builds the core functionality, tests important workflows, prepares the system for deployment, and documents how the system should be managed after launch.\n\n"
        "Practical Lessons\n"
        "- Start with a clear problem statement and target user.\n"
        "- Choose tools that match the project requirements, not just tools that are popular.\n"
        "- Keep sensitive values in environment variables.\n"
        "- Test the most important user workflows before deployment.\n"
        "- Document setup, deployment, and admin usage so the project can be maintained.\n"
        "- Treat security, persistence, media storage, and backups as part of the project, not afterthoughts.\n\n"
        "Professional Takeaways\n"
        f"The biggest takeaway from {title_lower} is that technical growth becomes more valuable when it is connected to real outcomes. A well-documented project can show problem-solving ability, backend skill, deployment knowledge, security awareness, and communication strength.\n\n"
        "Conclusion\n"
        f"{title} is a strong example of learning through building. By explaining the purpose, process, tools, and lessons, the blog becomes useful not only as a record of work but also as a guide for other learners and collaborators.\n\n"
        "SEO Title Ideas:\n"
        f"- {title} | TIPKODES TECH LAB\n"
        f"- Practical Lessons from {title}\n"
        f"- A Professional Guide to {title}\n\n"
        "Suggested Tags: Django, Python, Cybersecurity, Cloud, Portfolio, Deployment, Learning\n\n"
        f"Admin Notes Used:\n{title}\n\n"
        f"Research Notes:\n{research_note}\n\n"
        f"Site Context Used:\n{project_context}"
    )


def _local_response(question, context):
    lines = [line.strip() for line in context.splitlines() if line.strip()]
    normalized = " ".join(question.lower().strip().split())
    words = [word.lower().strip(".,:;!?()[]") for word in question.split() if len(word) > 2]

    if "admin content task:" in normalized:
        notes = question.split("Extra notes:", 1)[-1].strip() if "Extra notes:" in question else question
        source = context.strip() or notes or "TIPKODES TECH LAB portfolio content"
        if "draft_blog" in normalized or "draft a blog" in normalized or "write a blog" in normalized or "blog post" in normalized:
            return AIResponse(_local_blog_draft(notes, context), "local", "admin-draft-fallback")
        if "seo_titles" in normalized:
            return AIResponse(
                (
                    "SEO Title Suggestions:\n"
                    f"- {notes or 'TIPKODES TECH LAB Project'}: Practical Lessons and Key Takeaways\n"
                    f"- How {notes or 'This Project'} Shows Real Technical Growth\n"
                    f"- Building, Learning, and Documenting {notes or 'Technology Projects'}\n\n"
                    "Meta Description:\n"
                    "Explore a practical TIPKODES TECH LAB entry covering the problem, tools, lessons learned, and next steps."
                ),
                "local",
                "admin-draft-fallback",
            )
        if "summarize" in normalized or "summary" in normalized:
            return AIResponse(
                f"Summary:\n{source[:1200]}\n\nKey Points:\n- Main idea documented for portfolio visitors.\n- Useful for learning evidence and professional presentation.\n- Can be improved with screenshots, links, tags, and next steps.",
                "local",
                "admin-draft-fallback",
            )
        return AIResponse(
            (
                "AI Draft:\n"
                f"{source[:1200]}\n\n"
                "Suggested Improvement:\n"
                "Rewrite the content with a clear problem statement, tools used, implementation details, lessons learned, and next steps."
            ),
            "local",
            "admin-draft-fallback",
        )

    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
    if normalized in greetings or normalized.startswith(("hi ", "hello ", "hey ")):
        return AIResponse(
            "Hello, welcome to TIPKODES TECH LAB. I can help you explore Raphael's projects, skills, cybersecurity findings, Python work, cloud content, videos, certificates, resume, or contact details. What would you like to see?",
            "local",
            "conversational-fallback",
        )

    if normalized in {"hmm", "hm", "okay", "ok", "alright", "wow"}:
        return AIResponse(
            "I am here with you. You can ask me things like: what projects has Raphael built, what skills does he have, what cybersecurity findings are available, show me Python content, show cloud content, list videos, or how can I contact him.",
            "local",
            "conversational-fallback",
        )

    correction_phrases = ["wrong", "not correct", "incorrect", "no that", "nope", "that is not", "that's not"]
    if any(phrase in normalized for phrase in correction_phrases):
        return AIResponse(
            "Thanks for correcting me. Tell me what you want me to focus on, for example: projects Raphael has built, Python work, cybersecurity findings, cloud content, videos, certificates, skills, or contact details.",
            "local",
            "conversational-fallback",
        )

    if any(phrase in normalized for phrase in ["who are you", "what can you do", "help", "how can you help"]):
        return AIResponse(
            "I am the TIPKODES AI Assistant. I can guide visitors through the portfolio, recommend relevant projects or posts, explain cybersecurity findings, summarize videos and certificates, and point people to contact details when they want to connect.",
            "local",
            "conversational-fallback",
        )

    if any(phrase in normalized for phrase in ["contact", "email", "reach", "message", "connect"]):
        contact_lines = [line for line in lines if line.lower().startswith("contact:")]
        if contact_lines:
            return AIResponse(f"You can connect through the contact page. {contact_lines[0]}", "local", "conversational-fallback")
        return AIResponse("You can use the contact page to send Raphael a message directly.", "local", "conversational-fallback")

    compact = normalized.replace(" ", "")
    lab_intent = "lab" in normalized or "labs" in normalized or "available" in normalized
    if lab_intent:
        sections = [
            ("Projects", "Project:"),
            ("Cybersecurity findings", "Cyber finding:"),
            ("Python posts", "Python:"),
            ("Cloud posts", "Cloud:"),
            ("Videos", "Video:"),
            ("Certificates", "Certificate:"),
            ("Skills", "Skill:"),
            ("Career tracks", "Career track:"),
        ]
        available = []
        for label, prefix in sections:
            total = sum(1 for line in lines if line.startswith(prefix))
            available.append(f"- {label}: {total} item(s)")
        return AIResponse("These lab areas are available on TIPKODES TECH LAB:\n" + "\n".join(available), "local", "conversational-fallback")

    explicit_topics = [
        (
            ("project", "projects", "built", "build", "created", "developed", "portfolio platform"),
            "Project:",
            "Here are projects Raphael has built or documented on TIPKODES TECH LAB:",
            "I do not see project records available in the site context yet. Once projects are added in Admin, I can list them here with descriptions, technologies, and status.",
        ),
        (
            ("finding", "findings", "vulnerability", "vulnerabilities", "cybersecurity finding"),
            "Cyber finding:",
            "Here are cybersecurity findings or notes from the lab:",
            "I do not see public cybersecurity finding records yet. Once findings are added in Admin and marked public, I can list them here.",
        ),
        (
            ("certificate", "certificates", "certification", "certifications", "certif"),
            "Certificate:",
            "Here are certificates listed on the site:",
            "I do not see certificate records yet. Once certificates are added in Admin, I can list them here with issuer and credential details.",
        ),
        (
            ("skill", "skills"),
            "Skill:",
            "Here are some skills listed on the site:",
            "I do not see skill records yet. Once skills are added in Admin, I can list them here.",
        ),
        (
            ("python",),
            "Python:",
            "Here are Python-related entries:",
            "I do not see Python content records yet. Once Python posts are added in Admin, I can list them here.",
        ),
        (
            ("cloud", "aws"),
            "Cloud:",
            "Here are cloud computing entries:",
            "I do not see cloud content records yet. Once cloud posts are added in Admin, I can list them here.",
        ),
        (
            ("video", "videos", "youtube"),
            "Video:",
            "Here are videos from the lab:",
            "I do not see video records yet. Once videos are added in Admin, I can list them here.",
        ),
    ]
    for keywords, prefix, intro, empty_message in explicit_topics:
        if any(keyword in normalized or keyword in compact for keyword in keywords):
            topic_lines = [line for line in lines if line.startswith(prefix)]
            if topic_lines:
                answer = "\n".join(f"- {line}" for line in topic_lines[:6])
                return AIResponse(f"{intro}\n{answer}", "local", "conversational-fallback")
            return AIResponse(empty_message, "local", "conversational-fallback")

    topic_map = {
        "resume": ("Resume summary:", "Here is the resume summary:"),
        "about": ("Profile:", "Here is Raphael's profile summary:"),
        "raphael": ("Profile:", "Here is Raphael's profile summary:"),
    }
    for keyword, (prefix, intro) in topic_map.items():
        if keyword in normalized:
            topic_lines = [line for line in lines if line.startswith(prefix)]
            if topic_lines:
                answer = "\n".join(f"- {line}" for line in topic_lines[:6])
                return AIResponse(f"{intro}\n{answer}", "local", "conversational-fallback")

    matches = []
    for line in lines:
        score = sum(1 for word in words if word in line.lower())
        if score:
            matches.append((score, line))
    matches.sort(reverse=True)
    if not matches or matches[0][0] < 2:
        return AIResponse(
            "I am not fully sure what you want me to open. Try asking: projects Raphael has built, available labs, cybersecurity findings, certificates, Python content, cloud content, videos, skills, resume, or contact details.",
            "local",
            "keyword-fallback",
        )
    answer = "\n".join(f"- {line}" for _score, line in matches[:6])
    return AIResponse(f"Here is what I found from TIPKODES TECH LAB:\n{answer}", "local", "keyword-fallback")


def run_ai(prompt, context="", channel=AIInteraction.Channel.PUBLIC_CHAT, session_key=""):
    settings = get_ai_settings()
    if not settings.is_enabled:
        response = AIResponse("The AI assistant is currently disabled.", "local", "disabled", False, "AI disabled")
        log_ai_interaction(channel, prompt, response, session_key)
        return response

    messages = [
        {"role": "system", "content": settings.system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nRequest:\n{prompt}".strip()},
    ]
    provider_choice = os.environ.get("AI_PROVIDER", settings.provider).strip().lower() or settings.provider
    providers = []
    if provider_choice == AISettings.Provider.GROQ:
        providers = [_call_groq]
    elif provider_choice == AISettings.Provider.GEMINI:
        providers = [_call_gemini]
    elif provider_choice == AISettings.Provider.LOCAL:
        providers = []
    else:
        if os.environ.get("GROQ_API_KEY", "").strip():
            providers.append(_call_groq)
        if os.environ.get("GEMINI_API_KEY", "").strip():
            providers.append(_call_gemini)

    last_error = ""
    for provider in providers:
        try:
            response = provider(messages, settings)
            log_ai_interaction(channel, prompt, response, session_key)
            return response
        except (HTTPError, URLError, TimeoutError, RuntimeError, KeyError, IndexError, json.JSONDecodeError) as exc:
            last_error = str(exc)

    response = _local_response(prompt, context)
    if last_error:
        response.error = last_error
    log_ai_interaction(channel, prompt, response, session_key)
    return response


def log_ai_interaction(channel, prompt, response, session_key=""):
    AIInteraction.objects.create(
        channel=channel,
        prompt=prompt[:6000],
        response=response.text[:6000],
        provider=response.provider,
        model=response.model,
        success=response.success,
        error=response.error[:1000],
        session_key=session_key or "",
    )


def build_site_context(query="", limit=None):
    settings = get_ai_settings()
    limit = limit or settings.max_context_items
    bits = []
    profile = Profile.objects.order_by("-updated_at").first()
    resume = Resume.objects.order_by("-updated_at").first()
    if profile:
        bits.append(f"Profile: {profile.full_name}. {profile.professional_title}. {profile.short_bio}")
        if profile.email or profile.location:
            bits.append(f"Contact: {profile.email} {profile.location}".strip())
    if resume:
        bits.append(f"Resume summary: {resume.professional_summary}")

    datasets = [
        ("Project", Project.objects.all(), ["title", "short_description", "technologies_used", "status"]),
        ("Blog", BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED), ["title", "short_excerpt", "author"]),
        ("Cyber finding", CyberFinding.objects.filter(is_public=True), ["title", "severity", "short_summary", "status"]),
        ("Python", PythonPost.objects.all(), ["title", "python_area", "description", "difficulty_level"]),
        ("Cloud", CloudPost.objects.all(), ["title", "cloud_provider", "description", "tools_used"]),
        ("Video", Video.objects.all(), ["title", "description"]),
        ("Certificate", Certificate.objects.all(), ["title", "issuing_organization", "description", "credential_id"]),
        ("Career track", CareerTrack.objects.all(), ["title", "short_description", "status", "progress_level"]),
        ("Skill", Skill.objects.all(), ["name", "skill_level", "description"]),
    ]
    for label, qs, fields in datasets:
        if query:
            q_filter = Q()
            for field in fields:
                q_filter |= Q(**{f"{field}__icontains": query})
            qs = qs.filter(q_filter)
        for obj in qs[:limit]:
            values = [str(getattr(obj, field, "") or "") for field in fields]
            bits.append(f"{label}: " + " | ".join(value for value in values if value))
    return "\n".join(bits[: max(limit * 3, 12)])


def content_context_for_model(model_name, object_id):
    model_map = {
        "project": Project,
        "blog": BlogPost,
        "finding": CyberFinding,
        "python": PythonPost,
        "cloud": CloudPost,
        "video": Video,
        "certificate": Certificate,
        "contact": ContactMessage,
    }
    model = model_map.get(model_name)
    if not model or not object_id:
        return ""
    obj = model.objects.filter(pk=object_id).first()
    if not obj:
        return ""
    fields = []
    for field in obj._meta.fields:
        if field.name in {"id", "created_at", "updated_at"}:
            continue
        value = getattr(obj, field.name, "")
        if value:
            fields.append(f"{field.verbose_name}: {value}")
    return "\n".join(fields[:20])


def contact_assistance(contact_message):
    prompt = (
        "Analyze this contact message. Return a concise category, priority, summary, "
        "and a professional suggested reply."
    )
    context = (
        f"Name: {contact_message.name}\nEmail: {contact_message.email}\n"
        f"Subject: {contact_message.subject}\nMessage: {contact_message.message}"
    )
    return run_ai(prompt, context, AIInteraction.Channel.CONTACT_ASSISTANT)

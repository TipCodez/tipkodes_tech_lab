import json
import os
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


def _local_response(question, context):
    lines = [line.strip() for line in context.splitlines() if line.strip()]
    normalized = " ".join(question.lower().strip().split())
    words = [word.lower().strip(".,:;!?()[]") for word in question.split() if len(word) > 2]

    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
    if normalized in greetings or normalized.startswith(("hi ", "hello ", "hey ")):
        return AIResponse(
            "Hello, welcome to TIPKODES TECH LAB. I can help you explore Raphael's projects, skills, cybersecurity findings, Python work, cloud content, videos, certificates, resume, or contact details. What would you like to see?",
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

    topic_map = {
        "project": ("Project:", "Here are some projects from TIPKODES TECH LAB:"),
        "skill": ("Skill:", "Here are some skills listed on the site:"),
        "cyber": ("Cyber finding:", "Here are cybersecurity findings or notes from the lab:"),
        "finding": ("Cyber finding:", "Here are cybersecurity findings or notes from the lab:"),
        "python": ("Python:", "Here are Python-related entries:"),
        "cloud": ("Cloud:", "Here are cloud computing entries:"),
        "video": ("Video:", "Here are videos from the lab:"),
        "certificate": ("Certificate:", "Here are certificates listed on the site:"),
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
    if not matches:
        return AIResponse(
            "I could not find a strong match in the site content yet. Try asking about projects, skills, cybersecurity findings, Python, cloud, certificates, videos, or contact details.",
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

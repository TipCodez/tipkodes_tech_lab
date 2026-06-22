from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date

from .forms import BlogCommentForm, CertificateVerificationForm, ContactForm, NewsletterSubscriptionForm
from .models import (
    BlogPost,
    CareerTrack,
    Category,
    Certificate,
    CloudPost,
    CyberFinding,
    ExternalProfile,
    GalleryImage,
    NewsletterSubscription,
    PageView,
    Profile,
    Project,
    PythonPost,
    Reaction,
    Resume,
    Skill,
    Testimonial,
    TimelineEvent,
    Video,
)


def paginate(request, queryset, per_page=9):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def filter_by_category(request, queryset):
    category = request.GET.get("category")
    if category:
        queryset = queryset.filter(category__slug=category)
    return queryset


def page_context(title, subtitle, queryset=None, categories=None):
    return {
        "page_title": title,
        "page_subtitle": subtitle,
        "categories": categories,
        "items": queryset,
    }


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_reaction_summary(obj):
    content_type = ContentType.objects.get_for_model(obj)
    counts = Reaction.objects.filter(content_type=content_type, object_id=obj.pk).values("reaction_type").annotate(total=Count("id"))
    summary = {choice: 0 for choice, _label in Reaction.ReactionType.choices}
    for row in counts:
        summary[row["reaction_type"]] = row["total"]
    return summary


def build_search_result(item, result_type, title, snippet, url, date):
    return {
        "item": item,
        "type": result_type,
        "title": title,
        "snippet": snippet,
        "url": url,
        "date": date,
    }


def simple_pdf_response(filename, title, lines):
    def pdf_escape(value):
        return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content_lines = [title, ""] + [line for line in lines if line is not None]
    text_ops = ["BT", "/F1 12 Tf", "72 760 Td", "18 TL"]
    for line in content_lines[:36]:
        text_ops.append(f"({pdf_escape(line)[:95]}) Tj")
        text_ops.append("T*")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    response = HttpResponse(bytes(pdf), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def home(request):
    stats = {
        "projects": Project.objects.count(),
        "blogs": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).count(),
        "findings": CyberFinding.objects.filter(is_public=True).count(),
        "certificates": Certificate.objects.count(),
        "skills": Skill.objects.count(),
        "videos": Video.objects.count(),
    }
    return render(
        request,
        "home.html",
        {
            "profile": Profile.objects.order_by("-updated_at").first(),
            "featured_projects": Project.objects.filter(featured=True)[:3],
            "latest_blogs": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)[:3],
            "latest_findings": CyberFinding.objects.filter(is_public=True)[:3],
            "featured_videos": Video.objects.filter(featured=True)[:3],
            "featured_certificates": Certificate.objects.filter(featured=True)[:4],
            "skills_preview": Skill.objects.select_related("category")[:10],
            "stats": stats,
            "newsletter_form": NewsletterSubscriptionForm(),
        },
    )


def about(request):
    return render(
        request,
        "about.html",
        {
            "profile": Profile.objects.order_by("-updated_at").first(),
            "site_resume": Resume.objects.order_by("-updated_at").first(),
        },
    )


def career_tracks(request):
    qs = filter_by_category(request, CareerTrack.objects.select_related("category"))
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(short_description__icontains=q) | Q(tools_used__icontains=q))
    return render(
        request,
        "career_tracks.html",
        page_context(
            "Career Tracks",
            "Cybersecurity, Python, cloud, AI, research, and software engineering paths.",
            paginate(request, qs),
            Category.objects.filter(category_type=Category.CategoryType.CAREER),
        ),
    )


def career_track_detail(request, slug):
    track = get_object_or_404(CareerTrack, slug=slug)
    return render(
        request,
        "career_track_detail.html",
        {
            "track": track,
            "related_projects": track.projects.all()[:6],
            "related_blogs": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED, full_content__icontains=track.title)[:4],
            "related_certificates": track.certificates.all()[:6],
        },
    )


def projects(request):
    qs = filter_by_category(request, Project.objects.select_related("category", "career_track"))
    q = request.GET.get("q")
    tech = request.GET.get("technology")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(short_description__icontains=q) | Q(full_description__icontains=q))
    if tech:
        qs = qs.filter(technologies_used__icontains=tech)
    return render(
        request,
        "projects.html",
        page_context("Projects", "Real-world builds, labs, research, automations, and deployment work.", paginate(request, qs), Category.objects.filter(category_type=Category.CategoryType.PROJECT)),
    )


def project_detail(request, slug):
    project = get_object_or_404(Project.objects.select_related("category", "career_track"), slug=slug)
    related_blogs = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).filter(Q(full_content__icontains=project.title) | Q(short_excerpt__icontains=project.title))[:4]
    return render(request, "project_detail.html", {"project": project, "related_blogs": related_blogs, "reaction_summary": get_reaction_summary(project)})


def project_report(request, slug):
    project = get_object_or_404(Project.objects.select_related("category", "career_track"), slug=slug)
    lines = [
        f"Status: {project.status}",
        f"Category: {project.category.name if project.category else 'Not set'}",
        f"Career Track: {project.career_track.title if project.career_track else 'Not linked'}",
        f"Technologies: {project.technologies_used or 'Not set'}",
        "",
        "Short Description:",
        project.short_description,
        "",
        "Problem Solved:",
        project.problem_solved or "Not provided.",
        "",
        "Key Features:",
        project.key_features or "Not provided.",
    ]
    return simple_pdf_response(f"{project.slug}-report.pdf", f"TIPKODES TECH LAB Project Report: {project.title}", lines)


def findings(request):
    qs = CyberFinding.objects.filter(is_public=True)
    q = request.GET.get("q")
    severity = request.GET.get("severity")
    vulnerability = request.GET.get("vulnerability")
    target = request.GET.get("target")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(short_summary__icontains=q) | Q(full_description__icontains=q))
    if severity:
        qs = qs.filter(severity=severity)
    if vulnerability:
        qs = qs.filter(vulnerability_type__icontains=vulnerability)
    if target:
        qs = qs.filter(target_type__icontains=target)
    return render(request, "findings.html", {"items": paginate(request, qs), "severity_choices": CyberFinding.Severity.choices, "page_title": "Cybersecurity Findings", "page_subtitle": "Ethical findings, lab reports, learning writeups, and responsible disclosure notes."})


def finding_detail(request, slug):
    return render(request, "finding_detail.html", {"finding": get_object_or_404(CyberFinding, slug=slug, is_public=True)})


def python_career(request):
    qs = PythonPost.objects.all()
    q = request.GET.get("q")
    area = request.GET.get("area")
    difficulty = request.GET.get("difficulty")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(code_snippet__icontains=q))
    if area:
        qs = qs.filter(python_area__icontains=area)
    if difficulty:
        qs = qs.filter(difficulty_level=difficulty)
    return render(request, "python_career.html", {"items": paginate(request, qs), "difficulty_choices": PythonPost.Difficulty.choices})


def cloud_computing(request):
    qs = filter_by_category(request, CloudPost.objects.select_related("category"))
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(tools_used__icontains=q) | Q(steps_notes__icontains=q))
    return render(request, "cloud_computing.html", {"items": paginate(request, qs), "categories": Category.objects.filter(category_type=Category.CategoryType.CLOUD), "featured_items": CloudPost.objects.filter(featured=True)[:3]})


def blog(request):
    qs = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).select_related("category").prefetch_related("tags")
    qs = filter_by_category(request, qs)
    q = request.GET.get("q")
    tag = request.GET.get("tag")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(short_excerpt__icontains=q) | Q(full_content__icontains=q))
    if tag:
        qs = qs.filter(tags__slug=tag)
    return render(request, "blog.html", {"items": paginate(request, qs.distinct()), "categories": Category.objects.filter(category_type=Category.CategoryType.BLOG)})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost.objects.prefetch_related("tags"), slug=slug, status=BlogPost.Status.PUBLISHED)
    comment_form = BlogCommentForm(request.POST or None)
    if request.method == "POST" and comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.save()
        messages.success(request, "Your comment was submitted and is waiting for approval.")
        return redirect(post.get_absolute_url())
    related = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED, category=post.category).exclude(pk=post.pk)[:3]
    return render(
        request,
        "blog_detail.html",
        {
            "post": post,
            "related_posts": related,
            "comment_form": comment_form,
            "comments": post.comments.filter(is_approved=True),
            "reaction_summary": get_reaction_summary(post),
        },
    )


def gallery(request):
    qs = filter_by_category(request, GalleryImage.objects.select_related("category"))
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    return render(request, "gallery.html", {"items": paginate(request, qs, 12), "categories": Category.objects.filter(category_type=Category.CategoryType.GALLERY)})


def videos(request):
    qs = filter_by_category(request, Video.objects.select_related("category"))
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    return render(request, "videos.html", {"items": paginate(request, qs), "categories": Category.objects.filter(category_type=Category.CategoryType.VIDEO)})


def video_detail(request, slug):
    video = get_object_or_404(Video, slug=slug)
    return render(request, "video_detail.html", {"video": video, "reaction_summary": get_reaction_summary(video)})


def certificates(request):
    qs = filter_by_category(request, Certificate.objects.select_related("category", "related_career_track"))
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(issuing_organization__icontains=q) | Q(description__icontains=q))
    return render(request, "certificates.html", {"items": paginate(request, qs, 12), "categories": Category.objects.filter(category_type=Category.CategoryType.CERTIFICATE)})


def verify_certificate(request):
    form = CertificateVerificationForm(request.GET or None)
    certificate = None
    searched = False
    if form.is_valid():
        searched = True
        credential_id = form.cleaned_data["credential_id"].strip()
        certificate = Certificate.objects.filter(credential_id__iexact=credential_id).first()
    return render(request, "certificate_verify.html", {"form": form, "certificate": certificate, "searched": searched})


def skills(request):
    category = request.GET.get("category")
    qs = Skill.objects.select_related("category").prefetch_related("related_projects")
    if category:
        qs = qs.filter(category__slug=category)
    grouped = qs.values("category__name").annotate(total=Count("id")).order_by("category__name")
    return render(request, "skills.html", {"skills": qs, "groups": grouped, "categories": Category.objects.filter(category_type=Category.CategoryType.SKILL)})


def resume(request):
    return render(request, "resume.html", {"resume": Resume.objects.order_by("-updated_at").first()})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        message = form.save()
        if getattr(settings, "EMAIL_HOST", "") and getattr(settings, "DEFAULT_FROM_EMAIL", ""):
            send_mail(
                subject=f"New TIPKODES TECH LAB message: {message.subject}",
                message=f"From: {message.name} <{message.email}>\n\n{message.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        messages.success(request, "Your message has been saved. I will get back to you soon.")
        return redirect("contact")
    return render(request, "contact.html", {"form": form, "profile": Profile.objects.order_by("-updated_at").first()})


def testimonials(request):
    qs = Testimonial.objects.filter(is_public=True)
    return render(request, "testimonials.html", {"items": paginate(request, qs, 9)})


def timeline(request):
    qs = TimelineEvent.objects.filter(is_public=True)
    return render(request, "timeline.html", {"items": qs})


def integrations(request):
    profiles = ExternalProfile.objects.filter(is_active=True)
    return render(request, "integrations.html", {"profiles": profiles})


def deployment(request):
    stack = [
        ("Backend", "Django with SQLite development and PostgreSQL-ready DATABASE_URL."),
        ("Frontend", "Bootstrap 5, custom CSS, JavaScript animations, responsive templates."),
        ("Content", "Django Admin manages projects, findings, blogs, gallery, videos, certificates, skills, comments, testimonials, and timeline."),
        ("Security", "CSRF protection, upload validators, environment secrets, secure-cookie production switches, and custom errors."),
        ("Media", "Local media first with Cloudinary-ready environment variables."),
        ("Deployment", "Whitenoise static files, Gunicorn, PostgreSQL driver, HTTPS/HSTS environment controls."),
    ]
    return render(request, "deployment.html", {"stack": stack})


def subscribe_newsletter(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Newsletter subscription requires POST.")
    form = NewsletterSubscriptionForm(request.POST)
    if form.is_valid():
        subscription, created = NewsletterSubscription.objects.update_or_create(
            email=form.cleaned_data["email"],
            defaults={
                "name": form.cleaned_data.get("name", ""),
                "is_active": True,
                "source": request.POST.get("source", "website")[:120],
            },
        )
        if created:
            messages.success(request, "You are subscribed to TIPKODES TECH LAB updates.")
        else:
            messages.info(request, "Your newsletter subscription is active.")
    else:
        messages.error(request, "Please enter a valid email address.")
    return redirect(request.POST.get("next") or reverse("home"))


def react_to_content(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Reactions require POST.")

    model_map = {
        "project": Project,
        "blog": BlogPost,
        "video": Video,
        "certificate": Certificate,
    }
    model_name = request.POST.get("model")
    reaction_type = request.POST.get("reaction_type")
    object_id = request.POST.get("object_id")
    model = model_map.get(model_name)
    valid_reactions = {choice for choice, _label in Reaction.ReactionType.choices}

    if not model or reaction_type not in valid_reactions or not object_id:
        return HttpResponseBadRequest("Invalid reaction.")

    obj = get_object_or_404(model, pk=object_id)
    if not request.session.session_key:
        request.session.create()
    Reaction.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
        reaction_type=reaction_type,
        session_key=request.session.session_key,
        defaults={"ip_address": get_client_ip(request)},
    )
    messages.success(request, "Reaction saved.")
    return redirect(request.POST.get("next") or getattr(obj, "get_absolute_url", lambda: reverse("home"))())


def search_results(request):
    q = request.GET.get("q", "").strip()
    result_type = request.GET.get("type", "all")
    sort = request.GET.get("sort", "newest")
    date_from = parse_date(request.GET.get("from", "") or "")
    date_to = parse_date(request.GET.get("to", "") or "")
    results = []
    if q:
        search_sets = [
            (
                "project",
                Project.objects.filter(Q(title__icontains=q) | Q(short_description__icontains=q) | Q(full_description__icontains=q)),
                lambda item: build_search_result(item, "Project", item.title, item.short_description, item.get_absolute_url(), item.created_at.date()),
            ),
            (
                "blog",
                BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).filter(Q(title__icontains=q) | Q(short_excerpt__icontains=q) | Q(full_content__icontains=q)),
                lambda item: build_search_result(item, "Blog", item.title, item.short_excerpt, item.get_absolute_url(), (item.published_date or item.created_at).date()),
            ),
            (
                "finding",
                CyberFinding.objects.filter(is_public=True).filter(Q(title__icontains=q) | Q(short_summary__icontains=q) | Q(full_description__icontains=q)),
                lambda item: build_search_result(item, "Finding", item.title, item.short_summary, item.get_absolute_url(), item.created_at.date()),
            ),
            (
                "video",
                Video.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                lambda item: build_search_result(item, "Video", item.title, item.description, item.get_absolute_url(), item.created_at.date()),
            ),
            (
                "certificate",
                Certificate.objects.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(issuing_organization__icontains=q)),
                lambda item: build_search_result(item, "Certificate", item.title, item.description or item.issuing_organization, reverse("certificates"), item.created_at.date()),
            ),
            (
                "testimonial",
                Testimonial.objects.filter(is_public=True).filter(Q(name__icontains=q) | Q(role__icontains=q) | Q(organization__icontains=q) | Q(quote__icontains=q)),
                lambda item: build_search_result(item, "Testimonial", item.name, item.quote, reverse("testimonials"), item.created_at.date()),
            ),
            (
                "timeline",
                TimelineEvent.objects.filter(is_public=True).filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(category__icontains=q)),
                lambda item: build_search_result(item, "Timeline", item.title, item.description, reverse("timeline"), item.event_date),
            ),
            (
                "gallery",
                GalleryImage.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                lambda item: build_search_result(item, "Gallery", item.title, item.description, reverse("gallery"), item.created_at.date()),
            ),
            (
                "python",
                PythonPost.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                lambda item: build_search_result(item, "Python", item.title, item.description, reverse("python_career"), item.created_at.date()),
            ),
            (
                "cloud",
                CloudPost.objects.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(steps_notes__icontains=q)),
                lambda item: build_search_result(item, "Cloud", item.title, item.description, reverse("cloud_computing"), item.created_at.date()),
            ),
        ]
        for key, queryset, serializer in search_sets:
            if result_type not in ("all", key):
                continue
            for item in queryset:
                row = serializer(item)
                if date_from and row["date"] < date_from:
                    continue
                if date_to and row["date"] > date_to:
                    continue
                results.append(row)
        results.sort(key=lambda row: (row["title"].lower() if sort == "title" else row["date"]), reverse=(sort == "newest"))
    analytics = {
        "total_page_views": PageView.objects.count(),
        "popular_paths": PageView.objects.values("path").annotate(total=Count("id")).order_by("-total")[:5],
    }
    return render(
        request,
        "search_results.html",
        {
            "query": q,
            "selected_type": result_type,
            "selected_sort": sort,
            "date_from": request.GET.get("from", ""),
            "date_to": request.GET.get("to", ""),
            "items": paginate(request, results, 10),
            "analytics": analytics,
        },
    )


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)

from itertools import chain

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BlogCommentForm, ContactForm
from .models import (
    BlogPost,
    CareerTrack,
    Category,
    Certificate,
    CloudPost,
    CyberFinding,
    GalleryImage,
    Profile,
    Project,
    PythonPost,
    Resume,
    Skill,
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
            "profile": Profile.objects.first(),
            "featured_projects": Project.objects.filter(featured=True)[:3],
            "latest_blogs": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)[:3],
            "latest_findings": CyberFinding.objects.filter(is_public=True)[:3],
            "featured_videos": Video.objects.filter(featured=True)[:3],
            "featured_certificates": Certificate.objects.filter(featured=True)[:4],
            "skills_preview": Skill.objects.select_related("category")[:10],
            "stats": stats,
        },
    )


def about(request):
    return render(request, "about.html", {"profile": Profile.objects.first()})


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
    return render(request, "project_detail.html", {"project": project, "related_blogs": related_blogs})


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
    return render(request, "video_detail.html", {"video": get_object_or_404(Video, slug=slug)})


def certificates(request):
    qs = filter_by_category(request, Certificate.objects.select_related("category", "related_career_track"))
    q = request.GET.get("q")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(issuing_organization__icontains=q) | Q(description__icontains=q))
    return render(request, "certificates.html", {"items": paginate(request, qs, 12), "categories": Category.objects.filter(category_type=Category.CategoryType.CERTIFICATE)})


def skills(request):
    category = request.GET.get("category")
    qs = Skill.objects.select_related("category").prefetch_related("related_projects")
    if category:
        qs = qs.filter(category__slug=category)
    grouped = qs.values("category__name").annotate(total=Count("id")).order_by("category__name")
    return render(request, "skills.html", {"skills": qs, "groups": grouped, "categories": Category.objects.filter(category_type=Category.CategoryType.SKILL)})


def resume(request):
    return render(request, "resume.html", {"resume": Resume.objects.first()})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your message has been saved. I will get back to you soon.")
        return redirect("contact")
    return render(request, "contact.html", {"form": form, "profile": Profile.objects.first()})


def search_results(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        results = list(
            chain(
                Project.objects.filter(Q(title__icontains=q) | Q(short_description__icontains=q)),
                BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).filter(Q(title__icontains=q) | Q(short_excerpt__icontains=q)),
                CyberFinding.objects.filter(is_public=True).filter(Q(title__icontains=q) | Q(short_summary__icontains=q)),
                Video.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                Certificate.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                GalleryImage.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                PythonPost.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
                CloudPost.objects.filter(Q(title__icontains=q) | Q(description__icontains=q)),
            )
        )
    return render(request, "search_results.html", {"query": q, "items": paginate(request, results, 10)})


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)

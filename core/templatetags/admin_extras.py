from django import template

from core.models import (
    BlogComment,
    BlogPost,
    CareerTrack,
    Certificate,
    CloudPost,
    ContactMessage,
    CyberFinding,
    GalleryImage,
    Project,
    PythonPost,
    Skill,
    Video,
)


register = template.Library()


@register.simple_tag
def dashboard_stats():
    return {
        "projects": Project.objects.count(),
        "blogs": BlogPost.objects.count(),
        "published_blogs": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).count(),
        "findings": CyberFinding.objects.count(),
        "tracks": CareerTrack.objects.count(),
        "python_posts": PythonPost.objects.count(),
        "cloud_posts": CloudPost.objects.count(),
        "gallery": GalleryImage.objects.count(),
        "videos": Video.objects.count(),
        "certificates": Certificate.objects.count(),
        "skills": Skill.objects.count(),
        "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
        "pending_comments": BlogComment.objects.filter(is_approved=False).count(),
        "approved_comments": BlogComment.objects.filter(is_approved=True).count(),
    }

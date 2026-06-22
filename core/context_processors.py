from .models import Profile, Resume


def site_profile(request):
    return {
        "site_profile": Profile.objects.order_by("-updated_at").first(),
        "site_resume": Resume.objects.order_by("-updated_at").first(),
    }

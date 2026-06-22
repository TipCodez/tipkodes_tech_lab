from .models import Profile, Resume


def site_profile(request):
    return {
        "site_profile": Profile.objects.first(),
        "site_resume": Resume.objects.first(),
    }

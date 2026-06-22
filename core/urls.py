from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("career-tracks/", views.career_tracks, name="career_tracks"),
    path("career-tracks/<slug:slug>/", views.career_track_detail, name="career_track_detail"),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("projects/<slug:slug>/report/", views.project_report, name="project_report"),
    path("findings/", views.findings, name="findings"),
    path("findings/<slug:slug>/", views.finding_detail, name="finding_detail"),
    path("python-career/", views.python_career, name="python_career"),
    path("cloud-computing/", views.cloud_computing, name="cloud_computing"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("videos/", views.videos, name="videos"),
    path("videos/<slug:slug>/", views.video_detail, name="video_detail"),
    path("certificates/", views.certificates, name="certificates"),
    path("certificates/verify/", views.verify_certificate, name="verify_certificate"),
    path("skills/", views.skills, name="skills"),
    path("resume/", views.resume, name="resume"),
    path("testimonials/", views.testimonials, name="testimonials"),
    path("timeline/", views.timeline, name="timeline"),
    path("integrations/", views.integrations, name="integrations"),
    path("deployment/", views.deployment, name="deployment"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/subscribe/", views.subscribe_newsletter, name="subscribe_newsletter"),
    path("react/", views.react_to_content, name="react_to_content"),
    path("search/", views.search_results, name="search_results"),
]

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    BlogPost,
    CareerTrack,
    Category,
    Certificate,
    CloudPost,
    CyberFinding,
    Profile,
    Project,
    PythonPost,
    Resume,
    Skill,
    Tag,
    Video,
)


class Command(BaseCommand):
    help = "Create sample TIPKODES TECH LAB content for local development."

    def handle(self, *args, **options):
        categories = {
            ("Cybersecurity", "career"): Category.objects.get_or_create(name="Cybersecurity", category_type="career")[0],
            ("Python Development", "career"): Category.objects.get_or_create(name="Python Development", category_type="career")[0],
            ("Cloud Computing", "career"): Category.objects.get_or_create(name="Cloud Computing", category_type="career")[0],
            ("Cybersecurity Projects", "project"): Category.objects.get_or_create(name="Cybersecurity Projects", category_type="project")[0],
            ("Django Projects", "project"): Category.objects.get_or_create(name="Django Projects", category_type="project")[0],
            ("Cybersecurity", "blog"): Category.objects.get_or_create(name="Cybersecurity", category_type="blog")[0],
            ("Python", "blog"): Category.objects.get_or_create(name="Python", category_type="blog")[0],
            ("Cloud", "cloud"): Category.objects.get_or_create(name="Cloud", category_type="cloud")[0],
            ("Project Screenshots", "gallery"): Category.objects.get_or_create(name="Project Screenshots", category_type="gallery")[0],
            ("Project Demos", "video"): Category.objects.get_or_create(name="Project Demos", category_type="video")[0],
            ("Professional Training", "certificate"): Category.objects.get_or_create(name="Professional Training", category_type="certificate")[0],
            ("Programming", "skill"): Category.objects.get_or_create(name="Programming", category_type="skill")[0],
            ("Cloud Computing", "skill"): Category.objects.get_or_create(name="Cloud Computing", category_type="skill")[0],
            ("Tools", "skill"): Category.objects.get_or_create(name="Tools", category_type="skill")[0],
        }

        Profile.objects.get_or_create(
            full_name="TIPKODES",
            defaults={
                "professional_title": "Cybersecurity Student | Python Developer | Cloud Learner",
                "short_bio": "A personal technology lab for building, documenting, and showcasing real-world technical growth.",
                "biography": "TIPKODES TECH LAB brings together cybersecurity findings, Python projects, cloud notes, videos, certificates, research, and career progress in one admin-managed platform.",
                "technology_journey": "From programming fundamentals to Django applications, security labs, and cloud deployment practice.",
                "career_goals": "Grow into a cybersecurity-aware software engineer who builds useful, secure, and well-documented systems.",
                "tools_used": "Python, Django, Bootstrap, Git, Linux, VS Code, SQLite, PostgreSQL, AWS, Docker",
                "mission": "Build practical projects, learn in public, document progress, and turn technical effort into a clear professional portfolio.",
                "email": "hello@example.com",
                "location": "Ghana",
            },
        )

        security_track, _ = CareerTrack.objects.get_or_create(
            title="Cybersecurity Learning Path",
            defaults={
                "category": categories[("Cybersecurity", "career")],
                "short_description": "Ethical testing, vulnerability notes, labs, and responsible security learning.",
                "full_description": "This track documents practical cybersecurity growth through lab environments, authorized tests, CTF practice, and research writeups.",
                "icon": "bi bi-shield-lock",
                "skills_covered": "Web security, Linux, OWASP, reporting, responsible disclosure",
                "tools_used": "Burp Suite, Nmap, OWASP ZAP, Kali Linux",
                "progress_level": "Intermediate",
                "status": "Active",
            },
        )

        python_track, _ = CareerTrack.objects.get_or_create(
            title="Python Development Path",
            defaults={
                "category": categories[("Python Development", "career")],
                "short_description": "Python scripts, automation tools, Django apps, APIs, and learning notes.",
                "full_description": "This track follows Python growth from fundamentals to production-minded web applications and automation.",
                "icon": "bi bi-filetype-py",
                "skills_covered": "Python, Django, APIs, scripting, automation",
                "tools_used": "Python, Django, VS Code, Git",
                "progress_level": "Intermediate",
                "status": "Currently Learning",
            },
        )

        project, _ = Project.objects.get_or_create(
            title="TIPKODES TECH LAB Portfolio Platform",
            defaults={
                "category": categories[("Django Projects", "project")],
                "career_track": python_track,
                "short_description": "A Django portfolio lab for projects, findings, blogs, videos, certificates, and skills.",
                "full_description": "A full-stack Django and Bootstrap 5 platform designed to manage technical content through Django Admin and present it in a polished public website.",
                "problem_solved": "Keeps scattered learning evidence, project work, security notes, certificates, and media in one searchable portfolio system.",
                "key_features": "Admin-managed content, project showcase, global search, filters, pagination, media uploads, contact messages, responsive design.",
                "technologies_used": "Django, Python, Bootstrap 5, SQLite, JavaScript",
                "status": "In Progress",
                "featured": True,
            },
        )

        BlogPost.objects.get_or_create(
            title="Building a Personal Technology Lab with Django",
            defaults={
                "author": "TIPKODES",
                "category": categories[("Python", "blog")],
                "short_excerpt": "Why a portfolio can become a living lab for projects, research, and career evidence.",
                "full_content": "A strong technology portfolio should not only list work. It should explain the problems solved, tools used, lessons learned, and next steps. TIPKODES TECH LAB is built to support that workflow.",
                "reading_time": 4,
                "status": "Published",
                "published_date": timezone.now(),
                "featured": True,
            },
        )

        CyberFinding.objects.get_or_create(
            title="Sample Weak Security Header Report",
            defaults={
                "target_type": "Lab Environment",
                "target_name": "Local Django Test App",
                "vulnerability_type": "Weak Security Headers",
                "severity": "Low",
                "short_summary": "A sample authorized lab note showing how missing headers can be documented responsibly.",
                "full_description": "This placeholder demonstrates how security findings should be recorded with context, impact, reproduction notes, and recommended fixes.",
                "impact": "May reduce browser-side protection against clickjacking or content sniffing in some contexts.",
                "steps_to_reproduce": "Inspect response headers in a local test environment.",
                "recommended_fix": "Add secure middleware configuration and verify headers during deployment.",
                "tools_used": "Browser DevTools, securityheaders.com",
                "status": "Learning Report",
                "is_public": True,
            },
        )

        PythonPost.objects.get_or_create(
            title="Python File Organizer Script",
            defaults={
                "python_area": "Automation",
                "content_type": "Python Script",
                "description": "A sample automation entry for organizing files by extension.",
                "code_snippet": "from pathlib import Path\n\nfor file in Path('Downloads').iterdir():\n    print(file.suffix, file.name)",
                "difficulty_level": "Beginner",
                "related_project": project,
            },
        )

        CloudPost.objects.get_or_create(
            title="Hosting a Django App on a Cloud Platform",
            defaults={
                "cloud_provider": "General",
                "category": categories[("Cloud", "cloud")],
                "description": "A deployment note covering environment variables, static files, media storage, and database URLs.",
                "tools_used": "Django, Gunicorn, Whitenoise, PostgreSQL",
                "steps_notes": "Prepare environment variables, collect static files, connect a production database, and configure allowed hosts.",
                "related_project": project,
                "featured": True,
            },
        )

        Certificate.objects.get_or_create(
            title="Sample Cybersecurity Workshop Certificate",
            defaults={
                "issuing_organization": "TIPKODES Training Lab",
                "category": categories[("Professional Training", "certificate")],
                "description": "Placeholder certificate entry for local development.",
                "credential_id": "TTL-SAMPLE-001",
                "featured": True,
                "related_career_track": security_track,
            },
        )

        for name, category, level, icon in [
            ("Python", categories[("Programming", "skill")], "Intermediate", "bi bi-filetype-py"),
            ("Django", categories[("Programming", "skill")], "Intermediate", "bi bi-code-square"),
            ("Linux", categories[("Tools", "skill")], "Beginner", "bi bi-terminal"),
            ("Cloud Deployment", categories[("Cloud Computing", "skill")], "Beginner", "bi bi-cloud-upload"),
        ]:
            skill, _ = Skill.objects.get_or_create(name=name, defaults={"category": category, "skill_level": level, "icon": icon, "description": f"{name} practice and project experience."})
            skill.related_projects.add(project)

        Video.objects.get_or_create(
            title="Sample Project Demo",
            defaults={
                "category": categories[("Project Demos", "video")],
                "description": "Replace this with a real YouTube embed URL from your channel.",
                "youtube_embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "related_project": project,
                "featured": True,
            },
        )

        Resume.objects.get_or_create(
            full_name="TIPKODES",
            defaults={
                "professional_title": "Cybersecurity Student | Python Developer | Cloud Learner",
                "professional_summary": "A growing technology professional documenting cybersecurity, Python, Django, cloud computing, and real-world project experience.",
                "education": "Add your education details from Django Admin.",
                "experience": "Add internships, training, freelance, academic, or lab experience from Django Admin.",
                "technical_skills_summary": "Python, Django, Bootstrap, Linux, Git, security testing fundamentals, cloud deployment basics.",
                "projects_summary": "TIPKODES TECH LAB Portfolio Platform and other projects can be linked from the Projects module.",
                "certifications_summary": "Add certifications from the Certificates module.",
                "email": "hello@example.com",
                "location": "Ghana",
            },
        )

        Tag.objects.get_or_create(name="Django")
        Tag.objects.get_or_create(name="Cybersecurity")

        self.stdout.write(self.style.SUCCESS("Sample TIPKODES TECH LAB content created."))

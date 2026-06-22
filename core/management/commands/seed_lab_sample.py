from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import (
    BlogPost,
    CareerTrack,
    Category,
    Certificate,
    CloudPost,
    CyberFinding,
    ExternalProfile,
    Profile,
    Project,
    PythonPost,
    Resume,
    Skill,
    Tag,
    Testimonial,
    TimelineEvent,
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

        Profile.objects.update_or_create(
            full_name="Raphael Tibil Punobyin",
            defaults={
                "professional_title": "BSc. Computer Science Student | AWS Certified Cloud Practitioner | Cybersecurity Enthusiast | Python Developer",
                "short_bio": "BSc. Computer Science student at the University of Energy and Natural Resources with a strong passion for technology, Python backend development, networking, cybersecurity, online instruction, graphic design, and video editing.",
                "biography": "I am a BSc. Computer Science student at the University of Energy and Natural Resources with a strong passion for technology. As a Python developer and a networking and cybersecurity enthusiast, I enjoy exploring and building secure, efficient systems. I am also an online instructor, sharing my knowledge with others, and I have experience in graphic design and video editing, which allows me to bring a creative edge to technical projects.",
                "education": "BSc. Computer Science, University of Energy and Natural Resources.",
                "technology_journey": "My technology journey combines backend development with Django and FastAPI, cloud computing, cybersecurity, networking, online instruction, graphic design, and video editing.",
                "cybersecurity_journey": "I am building practical cybersecurity knowledge through networking fundamentals, secure system design, vulnerability research, and ethical lab practice.",
                "python_journey": "I use Python for backend development, automation, Django applications, FastAPI services, and practical problem-solving.",
                "cloud_journey": "As an AWS Certified Cloud Practitioner, I continue to build cloud computing knowledge through deployment, hosting, and cloud security practice.",
                "career_goals": "Grow into a strong backend and cybersecurity-aware cloud developer who builds secure, efficient, and creative technology solutions.",
                "tools_used": "Python, Django, FastAPI, AWS, Linux, Git, VS Code, PostgreSQL, SQLite, Bootstrap, graphic design tools, video editing tools",
                "mission": "Build secure and efficient systems, teach technology online, document real technical growth, and combine creativity with software engineering.",
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
                "author": "Raphael Tibil Punobyin",
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

        Testimonial.objects.get_or_create(
            name="Sample Mentor",
            defaults={
                "role": "Technology Mentor",
                "organization": "TIPKODES Network",
                "quote": "TIPKODES TECH LAB shows consistent learning, practical curiosity, and a strong habit of documenting technical growth.",
                "is_featured": True,
            },
        )

        TimelineEvent.objects.get_or_create(
            title="Started TIPKODES TECH LAB",
            defaults={
                "event_date": timezone.now().date(),
                "category": "Portfolio",
                "description": "Launched the Django-powered technology lab to document projects, cybersecurity findings, cloud learning, certificates, videos, and career growth.",
                "icon": "bi bi-rocket-takeoff",
            },
        )

        ExternalProfile.objects.get_or_create(
            platform="github",
            display_name="TIPKODES GitHub",
            defaults={
                "username": "TipCodez",
                "profile_url": "https://github.com/TipCodez",
                "headline": "Repositories, source code, and project history.",
                "public_items": 1,
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

        Resume.objects.update_or_create(
            full_name="Raphael Tibil Punobyin",
            defaults={
                "professional_title": "BSc. Computer Science Student | AWS Certified Cloud Practitioner | Cybersecurity Enthusiast | Python Developer",
                "professional_summary": "BSc. Computer Science student at the University of Energy and Natural Resources with a strong passion for technology. Python backend developer with Django and FastAPI experience, networking and cybersecurity enthusiast, AWS Certified Cloud Practitioner, online instructor, graphic designer, and video editor.",
                "education": "BSc. Computer Science, University of Energy and Natural Resources.",
                "experience": "Online instructor sharing technology knowledge, with practical experience in backend development, networking and cybersecurity learning, graphic design, and video editing.",
                "technical_skills_summary": "Python, Django, FastAPI, AWS Cloud, networking fundamentals, cybersecurity fundamentals, Linux, Git, Bootstrap, PostgreSQL, SQLite, graphic design, video editing.",
                "projects_summary": "TIPKODES TECH LAB Portfolio Platform and other projects can be linked from the Projects module.",
                "certifications_summary": "Add certifications from the Certificates module.",
                "email": "hello@example.com",
                "location": "Ghana",
            },
        )

        Tag.objects.get_or_create(name="Django")
        Tag.objects.get_or_create(name="Cybersecurity")

        self.stdout.write(self.style.SUCCESS("Sample TIPKODES TECH LAB content created."))

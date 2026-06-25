from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.text import slugify
from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse, urlunparse

from .validators import validate_image_file, validate_pdf_file


def normalize_youtube_embed_url(url):
    if not url:
        return url
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().replace("www.", "").replace("m.", "")
    path_parts = [part for part in parsed.path.split("/") if part]
    query = parse_qs(parsed.query)

    if "youtube-nocookie.com" in host and path_parts[:1] == ["embed"]:
        return url.strip()

    if "youtu.be" in host and path_parts:
        return f"https://www.youtube.com/embed/{path_parts[0]}"

    if "youtube.com" not in host:
        return url.strip()

    if path_parts[:1] == ["embed"] and len(path_parts) > 1:
        return f"https://www.youtube.com/embed/{path_parts[1]}"

    if path_parts[:1] in (["shorts"], ["live"]) and len(path_parts) > 1:
        return f"https://www.youtube.com/embed/{path_parts[1]}"

    video_id = query.get("v", [""])[0]
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"

    playlist_id = query.get("list", [""])[0]
    if playlist_id:
        return f"https://www.youtube.com/embed/videoseries?list={playlist_id}"

    return url.strip()


def youtube_embed_url_with_origin(url, origin):
    if not url or not origin:
        return url
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if "youtube.com" not in host and "youtube-nocookie.com" not in host:
        return url.strip()

    params = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key != "origin"]
    existing_keys = {key for key, value in params}
    if "rel" not in existing_keys:
        params.append(("rel", "0"))
    if "enablejsapi" not in existing_keys:
        params.append(("enablejsapi", "1"))
    params.append(("origin", origin.rstrip("/")))
    return urlunparse(parsed._replace(query=urlencode(params)))


def youtube_watch_url(url):
    if not url:
        return ""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    path_parts = [part for part in parsed.path.split("/") if part]
    query = parse_qs(parsed.query)

    if "youtu.be" in host and path_parts:
        return f"https://www.youtube.com/watch?v={path_parts[0]}"
    if "youtube.com" not in host and "youtube-nocookie.com" not in host:
        return url.strip()
    if path_parts[:1] == ["embed"] and len(path_parts) > 1:
        return f"https://www.youtube.com/watch?v={path_parts[1]}"
    if path_parts[:1] in (["shorts"], ["live"]) and len(path_parts) > 1:
        return f"https://www.youtube.com/watch?v={path_parts[1]}"

    video_id = query.get("v", [""])[0]
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    playlist_id = query.get("list", [""])[0]
    if playlist_id:
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    return url.strip()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SluggedModel(TimeStampedModel):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:210] or "item"
            slug = base
            counter = 2
            model = self.__class__
            while model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Profile(TimeStampedModel):
    full_name = models.CharField(max_length=160, default="Raphael Tibil Punobyin")
    professional_title = models.CharField(max_length=180, default="BSc. Computer Science Student | AWS Certified Cloud Practitioner | Cybersecurity Enthusiast | Python Developer")
    tagline = models.CharField(max_length=220, default="Cybersecurity, Python, Cloud Computing, and Real-World Tech Projects")
    short_bio = models.TextField(default="I am a BSc. Computer Science student at the University of Energy and Natural Resources with a strong passion for technology, Python backend development, networking, cybersecurity, online instruction, graphic design, and video editing.")
    biography = models.TextField(blank=True)
    education = models.TextField(blank=True)
    technology_journey = models.TextField(blank=True)
    cybersecurity_journey = models.TextField(blank=True)
    python_journey = models.TextField(blank=True)
    cloud_journey = models.TextField(blank=True)
    career_goals = models.TextField(blank=True)
    tools_used = models.TextField(blank=True, help_text="Comma-separated tools.")
    mission = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to="profile/", blank=True, validators=[validate_image_file])
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    github = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    snapchat = models.URLField(blank=True)
    whatsapp = models.URLField(blank=True)
    twitter = models.URLField(blank=True, verbose_name="X / Twitter")

    def __str__(self):
        return self.full_name


class Category(TimeStampedModel):
    class CategoryType(models.TextChoices):
        CAREER = "career", "Career Track"
        PROJECT = "project", "Project"
        BLOG = "blog", "Blog"
        GALLERY = "gallery", "Gallery"
        VIDEO = "video", "Video"
        CERTIFICATE = "certificate", "Certificate"
        SKILL = "skill", "Skill"
        CLOUD = "cloud", "Cloud"
        PYTHON = "python", "Python"
        FINDING = "finding", "Cyber Finding"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    category_type = models.CharField(max_length=30, choices=CategoryType.choices)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("slug", "category_type")
        ordering = ["category_type", "name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Tag(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CareerTrack(SluggedModel):
    class ProgressLevel(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"
        PROFESSIONAL = "Professional", "Professional"

    class Status(models.TextChoices):
        LEARNING = "Currently Learning", "Currently Learning"
        ACTIVE = "Active", "Active"
        COMPLETED = "Completed", "Completed"
        PAUSED = "Paused", "Paused"

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "career"})
    short_description = models.CharField(max_length=280)
    full_description = models.TextField()
    icon = models.CharField(max_length=80, blank=True, help_text="Bootstrap Icon class, e.g. bi-shield-lock.")
    banner_image = models.ImageField(upload_to="career_tracks/", blank=True, validators=[validate_image_file])
    skills_covered = models.TextField(blank=True)
    tools_used = models.TextField(blank=True)
    progress_level = models.CharField(max_length=30, choices=ProgressLevel.choices, default=ProgressLevel.BEGINNER)
    start_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.LEARNING)

    class Meta:
        ordering = ["title"]

    def get_absolute_url(self):
        return reverse("career_track_detail", kwargs={"slug": self.slug})


class Project(SluggedModel):
    class Status(models.TextChoices):
        COMPLETED = "Completed", "Completed"
        IN_PROGRESS = "In Progress", "In Progress"
        PLANNED = "Planned", "Planned"
        RESEARCH = "Research Stage", "Research Stage"
        TESTING = "Testing Stage", "Testing Stage"
        DEPLOYED = "Deployed", "Deployed"

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "project"})
    career_track = models.ForeignKey(CareerTrack, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    problem_solved = models.TextField(blank=True)
    key_features = models.TextField(blank=True)
    technologies_used = models.CharField(max_length=260, blank=True)
    main_image = models.ImageField(upload_to="projects/", blank=True, validators=[validate_image_file])
    github_link = models.URLField(blank=True)
    live_demo_link = models.URLField(blank=True)
    video_demo_link = models.URLField(blank=True)
    pdf_documentation = models.FileField(upload_to="projects/docs/", blank=True, validators=[validate_pdf_file])
    date_started = models.DateField(null=True, blank=True)
    date_completed = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_PROGRESS)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-featured", "-created_at"]

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/screenshots/", validators=[validate_image_file])
    caption = models.CharField(max_length=180, blank=True)

    def __str__(self):
        return self.caption or f"Screenshot for {self.project}"


class CyberFinding(SluggedModel):
    class Severity(models.TextChoices):
        INFO = "Informational", "Informational"
        LOW = "Low", "Low"
        MEDIUM = "Medium", "Medium"
        HIGH = "High", "High"
        CRITICAL = "Critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "Open", "Open"
        FIXED = "Fixed", "Fixed"
        LEARNING = "Learning Report", "Learning Report"
        REVIEW = "Under Review", "Under Review"
        NA = "Not Applicable", "Not Applicable"

    target_type = models.CharField(max_length=120, blank=True)
    target_name = models.CharField(max_length=160, blank=True)
    vulnerability_type = models.CharField(max_length=160)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    short_summary = models.CharField(max_length=300)
    full_description = models.TextField()
    impact = models.TextField(blank=True)
    steps_to_reproduce = models.TextField(blank=True)
    proof_screenshot = models.ImageField(upload_to="findings/", blank=True, validators=[validate_image_file])
    recommended_fix = models.TextField(blank=True)
    tools_used = models.CharField(max_length=260, blank=True)
    date_discovered = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.LEARNING)
    pdf_report = models.FileField(upload_to="findings/reports/", blank=True, validators=[validate_pdf_file])
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_discovered", "-created_at"]

    def get_absolute_url(self):
        return reverse("finding_detail", kwargs={"slug": self.slug})


class BlogPost(SluggedModel):
    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        PUBLISHED = "Published", "Published"
        ARCHIVED = "Archived", "Archived"

    author = models.CharField(max_length=120, default="TIPKODES")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "blog"})
    tags = models.ManyToManyField(Tag, blank=True)
    featured_image = models.ImageField(upload_to="blogs/", blank=True, validators=[validate_image_file])
    short_excerpt = models.CharField(max_length=320)
    full_content = models.TextField()
    reading_time = models.PositiveIntegerField(default=3, help_text="Minutes")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_date = models.DateTimeField(null=True, blank=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-featured", "-published_date", "-created_at"]

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})


class BlogComment(TimeStampedModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=120)
    email = models.EmailField()
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"


class Certificate(SluggedModel):
    issuing_organization = models.CharField(max_length=180)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "certificate"})
    description = models.TextField(blank=True)
    certificate_image = models.ImageField(upload_to="certificates/", blank=True, validators=[validate_image_file])
    certificate_pdf = models.FileField(upload_to="certificates/pdfs/", blank=True, validators=[validate_pdf_file])
    verification_link = models.URLField(blank=True)
    date_issued = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=120, blank=True)
    featured = models.BooleanField(default=False)
    related_career_track = models.ForeignKey(CareerTrack, on_delete=models.SET_NULL, null=True, blank=True, related_name="certificates")

    class Meta:
        ordering = ["-featured", "-date_issued", "-created_at"]


class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=140)
    role = models.CharField(max_length=160, blank=True)
    organization = models.CharField(max_length=160, blank=True)
    quote = models.TextField()
    photo = models.ImageField(upload_to="testimonials/", blank=True, validators=[validate_image_file])
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.name


class TimelineEvent(TimeStampedModel):
    title = models.CharField(max_length=180)
    event_date = models.DateField()
    category = models.CharField(max_length=80, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=80, blank=True)
    link = models.URLField(blank=True)
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    def __str__(self):
        return self.title


class ExternalProfile(TimeStampedModel):
    class Platform(models.TextChoices):
        GITHUB = "github", "GitHub"
        YOUTUBE = "youtube", "YouTube"

    platform = models.CharField(max_length=20, choices=Platform.choices)
    display_name = models.CharField(max_length=140)
    profile_url = models.URLField()
    username = models.CharField(max_length=140, blank=True)
    headline = models.CharField(max_length=220, blank=True)
    followers = models.PositiveIntegerField(default=0)
    public_items = models.PositiveIntegerField(default=0, help_text="Repos for GitHub, videos for YouTube.")
    total_views = models.PositiveIntegerField(default=0)
    embed_url = models.URLField(blank=True, help_text="Optional YouTube channel or featured playlist embed URL.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["platform", "display_name"]

    def save(self, *args, **kwargs):
        if self.platform == self.Platform.YOUTUBE and self.embed_url:
            self.embed_url = normalize_youtube_embed_url(self.embed_url)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_platform_display()} - {self.display_name}"


class DeploymentEntry(TimeStampedModel):
    class Section(models.TextChoices):
        ARCHITECTURE = "architecture", "Architecture Card"
        CHECKLIST = "checklist", "Production Checklist"
        TARGET = "target", "Deployment Target"

    section = models.CharField(max_length=30, choices=Section.choices, default=Section.ARCHITECTURE)
    title = models.CharField(max_length=160)
    description = models.TextField()
    icon = models.CharField(max_length=80, blank=True, help_text="Optional Bootstrap Icon class, e.g. bi-cloud-check.")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["section", "sort_order", "title"]
        verbose_name_plural = "Deployment entries"

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"


class AISettings(TimeStampedModel):
    class Provider(models.TextChoices):
        AUTO = "auto", "Auto"
        GROQ = "groq", "Groq"
        GEMINI = "gemini", "Gemini"
        LOCAL = "local", "Local fallback"

    is_enabled = models.BooleanField(default=True)
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.AUTO)
    assistant_name = models.CharField(max_length=80, default="TIPKODES AI Assistant")
    welcome_message = models.CharField(max_length=240, default="Ask me about Raphael, projects, cybersecurity findings, Python, cloud, videos, certificates, or how to connect.")
    system_prompt = models.TextField(default="You are TIPKODES AI Assistant. Answer from the provided TIPKODES TECH LAB context. Be helpful, concise, honest, and direct users to the contact page when needed.")
    groq_model = models.CharField(max_length=80, default="llama-3.1-8b-instant")
    gemini_model = models.CharField(max_length=80, default="gemini-1.5-flash")
    max_context_items = models.PositiveIntegerField(default=18)

    class Meta:
        verbose_name = "AI settings"
        verbose_name_plural = "AI settings"

    def __str__(self):
        return self.assistant_name


class AIInteraction(TimeStampedModel):
    class Channel(models.TextChoices):
        PUBLIC_CHAT = "public_chat", "Public Chat"
        ADMIN_ASSISTANT = "admin_assistant", "Admin Assistant"
        SMART_SEARCH = "smart_search", "Smart Search"
        CONTACT_ASSISTANT = "contact_assistant", "Contact Assistant"
        CONTENT_SUMMARY = "content_summary", "Content Summary"

    channel = models.CharField(max_length=40, choices=Channel.choices)
    prompt = models.TextField()
    response = models.TextField(blank=True)
    provider = models.CharField(max_length=30, blank=True)
    model = models.CharField(max_length=100, blank=True)
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True)
    session_key = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_channel_display()} - {self.created_at:%Y-%m-%d %H:%M}"


class Skill(TimeStampedModel):
    class Level(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"
        PROFESSIONAL = "Professional", "Professional"

    name = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "skill"})
    skill_level = models.CharField(max_length=30, choices=Level.choices, default=Level.BEGINNER)
    icon = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    related_projects = models.ManyToManyField(Project, blank=True, related_name="skills")

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return self.name


class PythonPost(SluggedModel):
    class Difficulty(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"

    python_area = models.CharField(max_length=100)
    content_type = models.CharField(max_length=100)
    description = models.TextField()
    code_snippet = models.TextField(blank=True)
    github_link = models.URLField(blank=True)
    project_link = models.URLField(blank=True)
    image = models.ImageField(upload_to="python/", blank=True, validators=[validate_image_file])
    difficulty_level = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    date_created = models.DateField(null=True, blank=True)
    related_blog_post = models.ForeignKey(BlogPost, on_delete=models.SET_NULL, null=True, blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-date_created", "-created_at"]


class CloudPost(SluggedModel):
    cloud_provider = models.CharField(max_length=80, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "cloud"})
    description = models.TextField()
    tools_used = models.CharField(max_length=260, blank=True)
    architecture_diagram = models.ImageField(upload_to="cloud/", blank=True, validators=[validate_image_file])
    steps_notes = models.TextField(blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    related_blog_post = models.ForeignKey(BlogPost, on_delete=models.SET_NULL, null=True, blank=True)
    related_certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True)
    date_published = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-featured", "-date_published", "-created_at"]


class GalleryImage(SluggedModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "gallery"})
    image = models.ImageField(upload_to="gallery/", validators=[validate_image_file])
    description = models.TextField(blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    related_blog_post = models.ForeignKey(BlogPost, on_delete=models.SET_NULL, null=True, blank=True)
    related_finding = models.ForeignKey(CyberFinding, on_delete=models.SET_NULL, null=True, blank=True)
    date_uploaded = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date_uploaded", "-created_at"]


class Video(SluggedModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "video"})
    description = models.TextField(blank=True)
    youtube_embed_url = models.URLField()
    thumbnail_image = models.ImageField(upload_to="videos/", blank=True, validators=[validate_image_file])
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    related_blog_post = models.ForeignKey(BlogPost, on_delete=models.SET_NULL, null=True, blank=True)
    related_finding = models.ForeignKey(CyberFinding, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-featured", "-published_date", "-created_at"]

    def save(self, *args, **kwargs):
        self.youtube_embed_url = normalize_youtube_embed_url(self.youtube_embed_url)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("video_detail", kwargs={"slug": self.slug})


class Resume(TimeStampedModel):
    full_name = models.CharField(max_length=160)
    professional_title = models.CharField(max_length=180)
    professional_summary = models.TextField()
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    technical_skills_summary = models.TextField(blank=True)
    projects_summary = models.TextField(blank=True)
    certifications_summary = models.TextField(blank=True)
    cv_file = models.FileField(upload_to="resumes/", blank=True, validators=[validate_pdf_file])
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    github_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)
    whatsapp_link = models.URLField(blank=True)

    def __str__(self):
        return self.full_name


class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} from {self.name}"


class NewsletterSubscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class PageView(TimeStampedModel):
    path = models.CharField(max_length=260)
    page_title = models.CharField(max_length=220, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.path


class Reaction(TimeStampedModel):
    class ReactionType(models.TextChoices):
        LIKE = "like", "Like"
        INSIGHTFUL = "insightful", "Insightful"
        INSPIRED = "inspired", "Inspired"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    reaction_type = models.CharField(max_length=20, choices=ReactionType.choices)
    session_key = models.CharField(max_length=80)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ("content_type", "object_id", "reaction_type", "session_key")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_reaction_type_display()} on {self.content_object}"

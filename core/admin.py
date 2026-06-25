from django import forms
from django.contrib import admin
from django.utils import timezone

from .models import (
    AIInteraction,
    AISettings,
    BlogPost,
    BlogComment,
    CareerTrack,
    Category,
    Certificate,
    CloudPost,
    ContactMessage,
    CyberFinding,
    DeploymentEntry,
    ExternalProfile,
    GalleryImage,
    NewsletterSubscription,
    PageView,
    Profile,
    Project,
    ProjectImage,
    PythonPost,
    Reaction,
    Resume,
    Skill,
    Tag,
    Testimonial,
    TimelineEvent,
    Video,
)
from .ai import contact_assistance


admin.site.site_header = "TIPKODES TECH LAB Admin"
admin.site.site_title = "TIPKODES TECH LAB"
admin.site.index_title = "Content Management"
admin.site.index_template = "admin/index.html"


@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    list_display = ("assistant_name", "provider", "is_enabled", "updated_at")
    fieldsets = (
        ("Status", {"fields": ("is_enabled", "provider", "assistant_name", "welcome_message")}),
        ("Prompt", {"fields": ("system_prompt", "max_context_items")}),
        ("Models", {"fields": ("groq_model", "gemini_model")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ("channel", "provider", "model", "success", "created_at")
    list_filter = ("channel", "provider", "success", "created_at")
    search_fields = ("prompt", "response", "error")
    readonly_fields = ("channel", "prompt", "response", "provider", "model", "success", "error", "session_key", "created_at", "updated_at")


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_photo"].required = False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ("full_name", "professional_title", "email", "updated_at")
    search_fields = ("full_name", "professional_title", "short_bio")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("full_name", "professional_title", "tagline", "short_bio", "profile_photo")}),
        ("Story", {"fields": ("biography", "education", "technology_journey", "cybersecurity_journey", "python_journey", "cloud_journey", "career_goals", "tools_used", "mission")}),
        ("Contact", {"fields": ("email", "phone", "location")}),
        ("Social Media", {"fields": ("github", "facebook", "tiktok", "youtube", "linkedin", "twitter", "instagram", "snapchat", "whatsapp")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "created_at")
    list_filter = ("category_type",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(CareerTrack)
class CareerTrackAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "progress_level", "status", "start_date")
    list_filter = ("category", "progress_level", "status")
    search_fields = ("title", "short_description", "full_description", "tools_used")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectImageInline]
    list_display = ("title", "category", "career_track", "status", "featured", "updated_at")
    list_filter = ("category", "status", "featured", "career_track")
    search_fields = ("title", "short_description", "full_description", "technologies_used")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Overview", {"fields": ("title", "slug", "category", "career_track", "short_description", "full_description", "featured")}),
        ("Project Details", {"fields": ("problem_solved", "key_features", "technologies_used", "status", "date_started", "date_completed")}),
        ("Media and Links", {"fields": ("main_image", "github_link", "live_demo_link", "video_demo_link", "pdf_documentation")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(CyberFinding)
class CyberFindingAdmin(admin.ModelAdmin):
    list_display = ("title", "vulnerability_type", "severity", "target_type", "status", "is_public", "date_discovered")
    list_filter = ("severity", "vulnerability_type", "target_type", "status", "is_public")
    search_fields = ("title", "short_summary", "full_description", "target_name", "tools_used")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "status", "featured", "published_date")
    list_filter = ("category", "status", "featured", "tags")
    search_fields = ("title", "short_excerpt", "full_content", "author")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at")
    actions = ["publish_posts", "draft_posts", "archive_posts"]
    fieldsets = (
        ("Core Article", {"fields": ("title", "slug", "author", "category", "tags", "featured_image", "short_excerpt", "full_content")}),
        ("AI Enhancements", {"fields": ("ai_summary", "ai_key_takeaways")}),
        ("SEO and Sharing", {"fields": ("seo_title", "meta_description", "canonical_url", "og_image")}),
        ("Publishing", {"fields": ("reading_time", "status", "published_date", "featured")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )

    @admin.action(description="Publish selected blog posts")
    def publish_posts(self, request, queryset):
        updated = 0
        for post in queryset:
            post.status = BlogPost.Status.PUBLISHED
            if not post.published_date:
                post.published_date = timezone.now()
            post.save(update_fields=["status", "published_date", "slug", "updated_at"])
            updated += 1
        self.message_user(request, f"{updated} blog post(s) published.")

    @admin.action(description="Move selected blog posts to draft")
    def draft_posts(self, request, queryset):
        updated = queryset.update(status=BlogPost.Status.DRAFT)
        self.message_user(request, f"{updated} blog post(s) moved to draft.")

    @admin.action(description="Archive selected blog posts")
    def archive_posts(self, request, queryset):
        updated = queryset.update(status=BlogPost.Status.ARCHIVED)
        self.message_user(request, f"{updated} blog post(s) archived.")

    def save_model(self, request, obj, form, change):
        if obj.status == BlogPost.Status.PUBLISHED and not obj.published_date:
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.action(description="Approve selected comments")
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Unapprove selected comments")
def unapprove_comments(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at", "post")
    search_fields = ("name", "email", "comment", "post__title")
    readonly_fields = ("created_at", "updated_at")
    actions = [approve_comments, unapprove_comments]


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "date_uploaded")
    list_filter = ("category", "date_uploaded")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "featured", "published_date")
    list_filter = ("category", "featured")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("title", "issuing_organization", "category", "featured", "date_issued", "credential_id")
    list_filter = ("category", "featured", "issuing_organization")
    search_fields = ("title", "issuing_organization", "description", "credential_id")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "organization", "is_featured", "is_public", "created_at")
    list_filter = ("is_featured", "is_public", "created_at")
    search_fields = ("name", "role", "organization", "quote")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "category", "is_public")
    list_filter = ("category", "is_public", "event_date")
    search_fields = ("title", "description", "category")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ExternalProfile)
class ExternalProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "platform", "username", "followers", "public_items", "total_views", "is_active")
    list_filter = ("platform", "is_active")
    search_fields = ("display_name", "username", "headline", "profile_url")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DeploymentEntry)
class DeploymentEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "sort_order", "is_active", "updated_at")
    list_filter = ("section", "is_active")
    search_fields = ("title", "description", "icon")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("sort_order", "is_active")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "skill_level")
    list_filter = ("category", "skill_level")
    search_fields = ("name", "description")
    filter_horizontal = ("related_projects",)


@admin.register(PythonPost)
class PythonPostAdmin(admin.ModelAdmin):
    list_display = ("title", "python_area", "content_type", "difficulty_level", "date_created")
    list_filter = ("python_area", "content_type", "difficulty_level")
    search_fields = ("title", "description", "code_snippet")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(CloudPost)
class CloudPostAdmin(admin.ModelAdmin):
    list_display = ("title", "cloud_provider", "category", "featured", "date_published")
    list_filter = ("cloud_provider", "category", "featured")
    search_fields = ("title", "description", "tools_used", "steps_notes")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "professional_title", "email", "updated_at")
    search_fields = ("full_name", "professional_title", "professional_summary")
    readonly_fields = ("created_at", "updated_at")


@admin.action(description="Mark selected messages as read")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)


@admin.action(description="Generate AI assistance for selected messages")
def generate_contact_assistance(modeladmin, request, queryset):
    total = 0
    for message in queryset[:10]:
        contact_assistance(message)
        total += 1
    modeladmin.message_user(request, f"AI assistance generated for {total} contact message(s). Check AI interactions.")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at", "updated_at")
    actions = [mark_as_read, generate_contact_assistance]


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_active", "source", "created_at")
    list_filter = ("is_active", "source", "created_at")
    search_fields = ("email", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("path", "ip_address", "created_at")
    list_filter = ("created_at", "path")
    search_fields = ("path", "user_agent", "referrer")
    readonly_fields = ("path", "page_title", "ip_address", "user_agent", "referrer", "created_at", "updated_at")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("content_object", "reaction_type", "session_key", "created_at")
    list_filter = ("reaction_type", "created_at", "content_type")
    search_fields = ("session_key",)
    readonly_fields = ("content_type", "object_id", "reaction_type", "session_key", "ip_address", "created_at", "updated_at")

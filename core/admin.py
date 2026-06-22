from django.contrib import admin

from .models import (
    BlogPost,
    CareerTrack,
    Category,
    Certificate,
    CloudPost,
    ContactMessage,
    CyberFinding,
    GalleryImage,
    Profile,
    Project,
    ProjectImage,
    PythonPost,
    Resume,
    Skill,
    Tag,
    Video,
)


admin.site.site_header = "TIPKODES TECH LAB Admin"
admin.site.site_title = "TIPKODES TECH LAB"
admin.site.index_title = "Content Management"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "professional_title", "email", "updated_at")
    search_fields = ("full_name", "professional_title", "short_bio")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("full_name", "professional_title", "tagline", "short_bio", "profile_photo")}),
        ("Story", {"fields": ("biography", "education", "technology_journey", "cybersecurity_journey", "python_journey", "cloud_journey", "career_goals", "tools_used", "mission")}),
        ("Contact", {"fields": ("email", "phone", "location", "github", "linkedin", "whatsapp", "twitter")}),
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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at", "updated_at")
    actions = [mark_as_read]

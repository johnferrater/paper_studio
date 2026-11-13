from django.contrib import admin

from .models import Chapter, Project


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "adviser", "status", "deadline", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "abstract", "owner__username", "adviser__username")
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("project", "number", "title", "status")
    list_filter = ("status",)
    search_fields = ("title", "project__title")

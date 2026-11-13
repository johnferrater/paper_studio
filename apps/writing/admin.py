from django.contrib import admin

from .models import ChapterDraft, ChapterReview


@admin.register(ChapterDraft)
class ChapterDraftAdmin(admin.ModelAdmin):
    list_display = ("chapter", "version", "author", "is_submitted", "updated_at")
    list_filter = ("is_submitted",)
    search_fields = ("chapter__title", "author__username", "content")


@admin.register(ChapterReview)
class ChapterReviewAdmin(admin.ModelAdmin):
    list_display = ("chapter", "reviewer", "decision", "created_at")
    list_filter = ("decision",)
    search_fields = ("chapter__title", "reviewer__username", "feedback")

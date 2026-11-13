from django.contrib import admin

from .models import Citation


@admin.register(Citation)
class CitationAdmin(admin.ModelAdmin):
    list_display = ("source", "style", "project", "created_at")
    list_filter = ("style",)
    search_fields = ("source__title", "formatted_text", "project__title")

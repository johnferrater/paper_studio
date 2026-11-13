from django.contrib import admin

from .models import Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("title", "authors", "year", "source_type", "project")
    list_filter = ("source_type",)
    search_fields = ("title", "authors", "doi", "project__title")

from django.contrib import admin

from .models import AssistantMessage


@admin.register(AssistantMessage)
class AssistantMessageAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("project__title", "user__username", "content")

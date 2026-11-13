from django.contrib import admin

from .models import Supervision


@admin.register(Supervision)
class SupervisionAdmin(admin.ModelAdmin):
    list_display = ("teacher", "student", "project", "status", "created_at")
    list_filter = ("status",)
    search_fields = (
        "teacher__username",
        "student__username",
        "project__title",
    )

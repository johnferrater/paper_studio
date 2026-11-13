from django.conf import settings
from django.db import models


class Source(models.Model):
    class SourceType(models.TextChoices):
        BOOK = "BOOK", "Book"
        JOURNAL = "JOURNAL", "Journal article"
        WEBSITE = "WEBSITE", "Website"
        REPORT = "REPORT", "Report"
        THESIS = "THESIS", "Thesis"

    project = models.ForeignKey(
        "research.Project", on_delete=models.CASCADE, related_name="sources"
    )
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255, help_text="e.g. Dela Cruz, J.; Santos, M.")
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    source_type = models.CharField(
        max_length=20, choices=SourceType.choices, default=SourceType.JOURNAL
    )
    publisher = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    doi = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sources",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

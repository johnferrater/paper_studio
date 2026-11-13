from django.conf import settings
from django.db import models

from .formatting import format_citation


class Citation(models.Model):
    class Style(models.TextChoices):
        APA = "APA", "APA"
        MLA = "MLA", "MLA"

    project = models.ForeignKey(
        "research.Project", on_delete=models.CASCADE, related_name="citations"
    )
    source = models.ForeignKey(
        "sources.Source", on_delete=models.CASCADE, related_name="citations"
    )
    style = models.CharField(
        max_length=10, choices=Style.choices, default=Style.APA
    )
    formatted_text = models.TextField(blank=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.formatted_text or str(self.source)

    def save(self, *args, **kwargs):
        self.formatted_text = format_citation(self.source, self.style)
        super().save(*args, **kwargs)

from django.conf import settings
from django.db import models


class ChapterDraft(models.Model):
    chapter = models.ForeignKey(
        "research.Chapter", on_delete=models.CASCADE, related_name="drafts"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chapter_drafts",
    )
    content = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.chapter} - v{self.version}"


class ChapterReview(models.Model):
    class Decision(models.TextChoices):
        APPROVED = "APPROVED", "Approved"
        REVISION = "REVISION", "Revision requested"

    chapter = models.ForeignKey(
        "research.Chapter", on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chapter_reviews",
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.chapter} - {self.get_decision_display()}"

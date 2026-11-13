from django.conf import settings
from django.db import models
from django.urls import reverse


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        FOR_REVIEW = "FOR_REVIEW", "For review"
        APPROVED = "APPROVED", "Approved"
        ARCHIVED = "ARCHIVED", "Archived"

    BADGE_CLASSES = {
        Status.DRAFT: "badge--gray",
        Status.IN_PROGRESS: "badge--blue",
        Status.FOR_REVIEW: "badge--amber",
        Status.APPROVED: "badge--green",
        Status.ARCHIVED: "badge--gray",
    }

    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    adviser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advised_projects",
        limit_choices_to={"role": "TEACHER"},
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("research:project_detail", args=[self.pk])

    @property
    def badge_class(self):
        return self.BADGE_CLASSES.get(self.status, "badge--gray")


class Chapter(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        FOR_REVIEW = "FOR_REVIEW", "For review"
        APPROVED = "APPROVED", "Approved"
        REVISION = "REVISION", "Revision required"

    BADGE_CLASSES = {
        Status.DRAFT: "badge--gray",
        Status.FOR_REVIEW: "badge--amber",
        Status.APPROVED: "badge--green",
        Status.REVISION: "badge--red",
    }

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="chapters"
    )
    number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "number"], name="unique_chapter_number_per_project"
            )
        ]

    def __str__(self):
        return f"Chapter {self.number}: {self.title}"

    @property
    def badge_class(self):
        return self.BADGE_CLASSES.get(self.status, "badge--gray")

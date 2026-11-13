from django.conf import settings
from django.db import models


class Supervision(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supervisions_as_teacher",
        limit_choices_to={"role": "TEACHER"},
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supervisions_as_student",
        limit_choices_to={"role": "STUDENT"},
    )
    project = models.ForeignKey(
        "research.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervisions",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "student", "project"],
                name="unique_supervision_per_triple",
            )
        ]

    def __str__(self):
        return f"{self.teacher} supervises {self.student}"

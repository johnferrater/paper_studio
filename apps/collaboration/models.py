from django.conf import settings
from django.db import models


class ProjectMembership(models.Model):
    class Role(models.TextChoices):
        MEMBER = "MEMBER", "Member"
        LEADER = "LEADER", "Leader"

    project = models.ForeignKey(
        "research.Project", on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_member_per_project"
            )
        ]

    def __str__(self):
        return f"{self.user} in {self.project}"

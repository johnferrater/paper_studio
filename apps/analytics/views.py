from django.db.models import Count
from django.views.generic import TemplateView

from apps.accounts.models import User
from apps.citations.models import Citation
from apps.core.permissions import RoleRequiredMixin
from apps.research.models import Project
from apps.sources.models import Source


class AnalyticsDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "analytics/dashboard.html"
    allowed_roles = ("TEACHER", "ADMIN")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_count"] = Project.objects.count()
        context["source_count"] = Source.objects.count()
        context["citation_count"] = Citation.objects.count()
        context["user_count"] = User.objects.count()
        context["projects_by_status"] = (
            Project.objects.values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
        context["users_by_role"] = (
            User.objects.values("role")
            .annotate(total=Count("id"))
            .order_by("role")
        )
        status_labels = dict(Project.Status.choices)
        context["projects_by_status"] = [
            {
                "label": status_labels.get(row["status"], row["status"]),
                "total": row["total"],
            }
            for row in context["projects_by_status"]
        ]
        role_labels = dict(User.Role.choices)
        context["users_by_role"] = [
            {
                "label": role_labels.get(row["role"], row["role"]),
                "total": row["total"],
            }
            for row in context["users_by_role"]
        ]
        return context

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from apps.notifications.services import notify
from apps.research.models import Project

from .models import ProjectMembership


class CollaborationIndexView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "collaboration/index.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.exclude(status=Project.Status.ARCHIVED).select_related(
            "owner"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["rows"] = [
            {
                "project": project,
                "is_owner": project.owner_id == user.id,
                "is_member": project.memberships.filter(user=user).exists(),
                "member_count": project.memberships.count() + 1,
            }
            for project in context["projects"]
        ]
        return context


@require_POST
@login_required
def join(request, project_pk):
    if request.user.role != "STUDENT":
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_pk)
    if project.owner_id != request.user.id:
        _, created = ProjectMembership.objects.get_or_create(
            project=project, user=request.user
        )
        if created:
            notify(
                project.owner,
                f"{request.user.username} joined {project.title}.",
                project.get_absolute_url(),
            )
    return redirect(project.get_absolute_url())


@require_POST
@login_required
def leave(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    ProjectMembership.objects.filter(
        project=project, user=request.user
    ).delete()
    return redirect(project.get_absolute_url())

from django.db.models import Q
from django.shortcuts import get_object_or_404


def visible_projects(user):
    """Projects a user is allowed to see based on their role and membership."""
    from apps.research.models import Project

    if not user.is_authenticated:
        return Project.objects.none()
    if user.role == "ADMIN":
        return Project.objects.all()
    return Project.objects.filter(
        Q(owner=user) | Q(adviser=user) | Q(memberships__user=user)
    ).distinct()


def get_visible_project(user, pk):
    return get_object_or_404(visible_projects(user), pk=pk)

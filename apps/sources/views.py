from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView

from apps.core.access import get_visible_project, visible_projects

from .forms import SourceForm
from .models import Source


class SourceListView(LoginRequiredMixin, ListView):
    model = Source
    template_name = "sources/source_list.html"
    context_object_name = "sources"

    def get_queryset(self):
        return (
            Source.objects.filter(
                project__in=visible_projects(self.request.user)
            )
            .select_related("project")
        )


@login_required
def source_create(request, project_pk):
    project = get_visible_project(request.user, project_pk)
    if request.method == "POST":
        form = SourceForm(request.POST)
        if form.is_valid():
            source = form.save(commit=False)
            source.project = project
            source.created_by = request.user
            source.save()
            return redirect(project.get_absolute_url())
    else:
        form = SourceForm()

    return render(
        request,
        "sources/source_form.html",
        {"form": form, "project": project},
    )

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView

from apps.core.access import get_visible_project, visible_projects

from .forms import CitationForm
from .models import Citation


class CitationListView(LoginRequiredMixin, ListView):
    model = Citation
    template_name = "citations/citation_list.html"
    context_object_name = "citations"

    def get_queryset(self):
        return (
            Citation.objects.filter(
                project__in=visible_projects(self.request.user)
            )
            .select_related("project", "source")
        )


@login_required
def citation_create(request, project_pk):
    project = get_visible_project(request.user, project_pk)
    if request.method == "POST":
        form = CitationForm(request.POST, project=project)
        if form.is_valid():
            citation = form.save(commit=False)
            citation.project = project
            citation.created_by = request.user
            citation.save()
            return redirect(project.get_absolute_url())
    else:
        form = CitationForm(project=project)

    return render(
        request,
        "citations/citation_form.html",
        {"form": form, "project": project},
    )

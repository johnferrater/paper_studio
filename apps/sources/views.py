from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.shortcuts import redirect, render
from django.views.generic import ListView

from apps.core.access import get_visible_project, visible_projects

from .forms import SourceForm
from .models import Source


class SourceListView(LoginRequiredMixin, ListView):
    model = Source
    template_name = "sources/source_list.html"
    context_object_name = "sources"
    paginate_by = 15

    def get_queryset(self):
        queryset = Source.objects.filter(
            project__in=visible_projects(self.request.user)
        ).select_related("project")

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(authors__icontains=query)
                | Q(publisher__icontains=query)
                | Q(doi__icontains=query)
            )

        source_type = self.request.GET.get("type", "").strip()
        if source_type in Source.SourceType.values:
            queryset = queryset.filter(source_type=source_type)

        sort = self.request.GET.get("sort", "recent")
        if sort == "title":
            queryset = queryset.order_by("title")
        elif sort == "year":
            queryset = queryset.order_by(F("year").asc(nulls_last=True), "title")
        else:
            queryset = queryset.order_by("-created_at")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["source_type"] = self.request.GET.get("type", "").strip()
        context["sort"] = self.request.GET.get("sort", "recent")
        context["source_type_choices"] = Source.SourceType.choices
        return context


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

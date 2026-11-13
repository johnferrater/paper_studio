from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from apps.core.access import get_visible_project, visible_projects
from apps.core.permissions import StudentRequiredMixin

from .forms import ChapterForm, ProjectForm
from .models import Chapter, Project


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "research/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return visible_projects(self.request.user)


class ProjectCreateView(StudentRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "research/project_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    template_name = "research/project_detail.html"
    context_object_name = "project"

    def get_object(self, queryset=None):
        return get_visible_project(self.request.user, self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chapters"] = self.object.chapters.all()
        context["memberships"] = self.object.memberships.select_related("user")
        context["sources"] = self.object.sources.all()[:5]
        context["citations"] = self.object.citations.all()[:5]
        context["is_owner"] = self.object.owner_id == self.request.user.id
        context["is_member"] = self.object.memberships.filter(
            user=self.request.user
        ).exists()
        return context


class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = "research/chapter_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(
            visible_projects(request.user), pk=kwargs["project_pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("research:project_detail", args=[self.project.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import ListView

from apps.core.access import get_visible_project, visible_projects

from .models import AssistantMessage
from .services import ask_assistant


class AssistantIndexView(LoginRequiredMixin, ListView):
    template_name = "assistant/index.html"
    context_object_name = "projects"

    def get_queryset(self):
        return visible_projects(self.request.user)


@login_required
def chat(request, project_pk):
    project = get_visible_project(request.user, project_pk)
    history = list(
        AssistantMessage.objects.filter(
            project=project, user=request.user
        ).order_by("created_at")
    )

    if request.method == "POST":
        prompt = request.POST.get("q", "").strip()
        if prompt:
            reply = ask_assistant(project, history, prompt)
            AssistantMessage.objects.create(
                project=project,
                user=request.user,
                role=AssistantMessage.Role.USER,
                content=prompt,
            )
            AssistantMessage.objects.create(
                project=project,
                user=request.user,
                role=AssistantMessage.Role.ASSISTANT,
                content=reply,
            )
            return redirect("assistant:chat", project_pk=project.pk)

    return render(
        request,
        "assistant/chat.html",
        {"project": project, "messages": history},
    )

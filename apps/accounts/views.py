import os

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.collaboration.models import ProjectMembership
from apps.core.permissions import (
    AdminRequiredMixin,
    StudentRequiredMixin,
    TeacherRequiredMixin,
)
from apps.notifications.services import notify
from apps.research.models import Chapter, Project
from apps.writing.models import ChapterReview

from .forms import StudentSignUpForm
from .models import User

ROLE_HOME = {
    "STUDENT": "student_dashboard",
    "TEACHER": "teacher_dashboard",
    "ADMIN": "admin_dashboard",
}


def home_for(user):
    return ROLE_HOME.get(user.role, "login")


def home(request):
    if request.user.is_authenticated:
        return redirect(home_for(request.user))
    return redirect("login")


class RoleLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse(home_for(self.request.user))


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = StudentSignUpForm
    success_url = reverse_lazy("student_dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(home_for(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        return redirect(home_for(user))


class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = "student/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        projects = Project.objects.filter(
            Q(owner=user) | Q(memberships__user=user)
        ).distinct()
        context["projects"] = projects.select_related("owner", "adviser")[:5]
        context["project_count"] = projects.count()
        context["chapters"] = (
            Chapter.objects.filter(project__in=projects)
            .select_related("project")
            .order_by("project__title", "number")[:8]
        )
        revision_chapters = Chapter.objects.filter(
            project__in=projects, status=Chapter.Status.REVISION
        ).select_related("project")
        context["revision_chapters"] = revision_chapters
        context["revision_count"] = revision_chapters.count()
        context["notifications"] = user.notifications.all()[:5]
        return context


class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = "teacher/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        advised = Project.objects.filter(adviser=user).select_related("owner")
        pending = Chapter.objects.filter(
            project__in=advised, status=Chapter.Status.FOR_REVIEW
        ).select_related("project")
        owner_ids = set(advised.values_list("owner_id", flat=True))
        member_ids = set(
            ProjectMembership.objects.filter(project__in=advised).values_list(
                "user_id", flat=True
            )
        )
        context.update(
            {
                "projects": advised[:5],
                "project_count": advised.count(),
                "pending_chapters": pending[:8],
                "pending_count": pending.count(),
                "student_count": len(owner_ids | member_ids),
                "notifications": user.notifications.all()[:5],
            }
        )
        return context


class TeacherSubmissionsView(TeacherRequiredMixin, View):
    template_name = "teacher/submissions.html"

    def get(self, request):
        return render(request, self.template_name, self.get_context(request))

    def get_context(self, request):
        chapters = (
            Chapter.objects.filter(
                project__adviser=request.user,
                status=Chapter.Status.FOR_REVIEW,
            )
            .select_related("project", "project__owner")
            .order_by("project__title", "number")
        )
        selected = None
        draft = None
        reviews = []
        selected_id = request.GET.get("chapter")
        if selected_id:
            selected = get_object_or_404(chapters, pk=selected_id)
            draft = selected.drafts.first()
            reviews = selected.reviews.select_related("reviewer")
        return {
            "chapters": chapters,
            "selected": selected,
            "draft": draft,
            "reviews": reviews,
        }

    def post(self, request):
        grammar = (
            Chapter.objects.filter(project__adviser=request.user)
            .select_related("project")
        )
        chapter = get_object_or_404(grammar, pk=request.POST.get("chapter"))
        decision = request.POST.get("decision")
        valid = {
            ChapterReview.Decision.APPROVED,
            ChapterReview.Decision.REVISION,
        }
        if decision not in valid:
            messages.error(request, "Invalid review action.")
            return redirect("teacher_submissions")
        if chapter.status != Chapter.Status.FOR_REVIEW:
            messages.error(
                request, "Only chapters awaiting review can be reviewed."
            )
            return redirect("teacher_submissions")

        feedback = request.POST.get("feedback", "").strip()

        with transaction.atomic():
            locked = Chapter.objects.select_for_update().get(pk=chapter.pk)
            if locked.status != Chapter.Status.FOR_REVIEW:
                messages.error(
                    request, "This chapter is no longer awaiting review."
                )
                return redirect("teacher_submissions")

            ChapterReview.objects.create(
                chapter=locked,
                reviewer=request.user,
                decision=decision,
                feedback=feedback,
            )
            locked.status = (
                Chapter.Status.APPROVED
                if decision == ChapterReview.Decision.APPROVED
                else Chapter.Status.REVISION
            )
            locked.save(update_fields=["status", "updated_at"])

            if decision == ChapterReview.Decision.APPROVED:
                message = f"Your {locked} was approved."
            else:
                message = f"Revision requested for {locked}."
                if feedback:
                    message += f" Feedback: {feedback}"
            notify(
                locked.project.owner,
                message[:255],
                reverse("writing:chapter_edit", args=[locked.pk]),
            )

        messages.success(request, f"Feedback saved for {chapter}.")
        return redirect("teacher_submissions")


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "admin_panel/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_users": User.objects.count(),
                "students": User.objects.filter(role=User.Role.STUDENT).count(),
                "teachers": User.objects.filter(role=User.Role.TEACHER).count(),
                "admins": User.objects.filter(role=User.Role.ADMIN).count(),
                "project_count": Project.objects.count(),
                "recent_projects": Project.objects.select_related("owner")[:5],
                "notifications": self.request.user.notifications.all()[:5],
                "assistant_configured": bool(
                    os.environ.get("OPENAI_API_KEY", "").strip()
                ),
            }
        )
        return context

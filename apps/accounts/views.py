from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from apps.core.permissions import (
    AdminRequiredMixin,
    StudentRequiredMixin,
    TeacherRequiredMixin,
)

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


class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = "student/dashboard.html"


class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = "teacher/dashboard.html"


class TeacherSubmissionsView(TeacherRequiredMixin, TemplateView):
    template_name = "teacher/submissions.html"


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "admin_panel/dashboard.html"

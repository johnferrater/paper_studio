from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.RoleLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("student/", views.StudentDashboardView.as_view(), name="student_dashboard"),
    path("teacher/", views.TeacherDashboardView.as_view(), name="teacher_dashboard"),
    path("teacher/submissions/", views.TeacherSubmissionsView.as_view(), name="teacher_submissions"),
    path("manage/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
]

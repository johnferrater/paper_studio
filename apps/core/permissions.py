from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only users whose role is in allowed_roles may open the page."""

    allowed_roles = ()

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied  # logged in, wrong role -> 403
        return super().handle_no_permission()  # not logged in -> login page


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("STUDENT",)


class TeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("TEACHER",)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("ADMIN",)

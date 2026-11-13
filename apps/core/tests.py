from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, SimpleTestCase

from apps.core.permissions import (
    AdminRequiredMixin,
    StudentRequiredMixin,
    TeacherRequiredMixin,
)


class FakeUser:
    def __init__(self, role, authenticated=True):
        self.role = role
        self.is_authenticated = authenticated


class RoleRequiredMixinTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _mixin(self, mixin_class, user):
        mixin = mixin_class()
        request = self.factory.get("/")
        request.user = user
        mixin.request = request
        return mixin

    def test_allowed_roles_are_configured(self):
        self.assertEqual(StudentRequiredMixin.allowed_roles, ("STUDENT",))
        self.assertEqual(TeacherRequiredMixin.allowed_roles, ("TEACHER",))
        self.assertEqual(AdminRequiredMixin.allowed_roles, ("ADMIN",))

    def test_matching_role_passes(self):
        mixin = self._mixin(StudentRequiredMixin, FakeUser("STUDENT"))
        self.assertTrue(mixin.test_func())

    def test_non_matching_role_fails(self):
        mixin = self._mixin(StudentRequiredMixin, FakeUser("TEACHER"))
        self.assertFalse(mixin.test_func())

    def test_authenticated_wrong_role_raises_permission_denied(self):
        mixin = self._mixin(TeacherRequiredMixin, FakeUser("STUDENT"))
        with self.assertRaises(PermissionDenied):
            mixin.handle_no_permission()

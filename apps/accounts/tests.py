from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from apps.notifications.models import Notification
from apps.research.models import Chapter, Project

from .models import User
from .views import home, home_for


class FakeUser:
    def __init__(self, role, authenticated=True):
        self.role = role
        self.is_authenticated = authenticated


class HomeForTests(SimpleTestCase):
    def test_maps_each_role_to_its_dashboard(self):
        self.assertEqual(home_for(FakeUser("STUDENT")), "student_dashboard")
        self.assertEqual(home_for(FakeUser("TEACHER")), "teacher_dashboard")
        self.assertEqual(home_for(FakeUser("ADMIN")), "admin_dashboard")

    def test_unknown_role_falls_back_to_login(self):
        self.assertEqual(home_for(FakeUser("UNKNOWN")), "login")


class HomeViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_user_is_redirected_to_login(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        response = home(request)
        self.assertRedirects(
            response, reverse("login"), fetch_redirect_response=False
        )

    def test_authenticated_user_is_redirected_to_role_dashboard(self):
        request = self.factory.get("/")
        request.user = FakeUser("TEACHER")
        response = home(request)
        self.assertRedirects(
            response, reverse("teacher_dashboard"), fetch_redirect_response=False
        )


class RegistrationTests(TestCase):
    def test_self_registration_creates_a_student_and_logs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newbie",
                "first_name": "New",
                "last_name": "Bee",
                "email": "new@example.com",
                "password1": "Sup3rSecret!42",
                "password2": "Sup3rSecret!42",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newbie")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertIn("_auth_user_id", self.client.session)


class DashboardRenderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            "stud", password="pass12345", role="STUDENT"
        )
        cls.teacher = User.objects.create_user(
            "teach", password="pass12345", role="TEACHER"
        )
        cls.admin = User.objects.create_user(
            "admin", password="pass12345", role="ADMIN"
        )
        cls.project = Project.objects.create(
            title="Live project", owner=cls.student, adviser=cls.teacher
        )
        cls.chapter = Chapter.objects.create(
            project=cls.project,
            number=1,
            title="Introduction",
            status=Chapter.Status.FOR_REVIEW,
        )
        Notification.objects.create(recipient=cls.student, message="Welcome")

    def test_student_dashboard_renders(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_teacher_dashboard_renders(self):
        self.client.force_login(self.teacher)
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_renders(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)

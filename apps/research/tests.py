from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.collaboration.models import ProjectMembership

from .models import Project


class ProjectAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            "owner", password="pass12345", role="STUDENT"
        )
        cls.other = User.objects.create_user(
            "other", password="pass12345", role="STUDENT"
        )
        cls.teacher = User.objects.create_user(
            "teach", password="pass12345", role="TEACHER"
        )
        cls.project = Project.objects.create(
            title="Paper", owner=cls.owner, adviser=cls.teacher
        )

    def test_owner_can_view_project(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.project.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_non_member_cannot_view_project(self):
        self.client.force_login(self.other)
        response = self.client.get(self.project.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_member_can_view_project(self):
        ProjectMembership.objects.create(project=self.project, user=self.other)
        self.client.force_login(self.other)
        response = self.client.get(self.project.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_student_can_create_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("research:project_create"),
            {"title": "New paper", "abstract": "", "deadline": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Project.objects.filter(title="New paper", owner=self.owner).exists()
        )

    def test_teacher_cannot_create_project(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("research:project_create"),
            {"title": "Nope", "abstract": "", "deadline": ""},
        )
        self.assertEqual(response.status_code, 403)

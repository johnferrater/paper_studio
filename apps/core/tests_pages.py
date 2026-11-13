"""Smoke tests: every rendered page must load for each role.

These guard the shared templates and design-system partials against
referencing a context variable or URL name that no longer exists.
"""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.assistant.models import AssistantMessage
from apps.citations.models import Citation
from apps.collaboration.models import ProjectMembership
from apps.notifications.models import Notification
from apps.research.models import Chapter, Project
from apps.sources.models import Source
from apps.supervision.models import Supervision


class PageSmokeTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student", password="pass12345", role=User.Role.STUDENT
        )
        self.teacher = User.objects.create_user(
            username="teacher", password="pass12345", role=User.Role.TEACHER
        )
        self.admin = User.objects.create_user(
            username="admin", password="pass12345", role=User.Role.ADMIN
        )

        self.project = Project.objects.create(
            title="Impact of sleep on recall",
            abstract="A study of memory consolidation.",
            owner=self.student,
            adviser=self.teacher,
            status=Project.Status.IN_PROGRESS,
        )
        self.chapter = Chapter.objects.create(
            project=self.project, number=1, title="Introduction"
        )
        self.source = Source.objects.create(
            project=self.project,
            title="Sleep and memory",
            authors="Dela Cruz, J.; Santos, M.",
            year=2024,
            source_type=Source.SourceType.JOURNAL,
            created_by=self.student,
        )
        self.citation = Citation.objects.create(
            project=self.project,
            source=self.source,
            style=Citation.Style.APA,
            created_by=self.student,
        )
        ProjectMembership.objects.create(project=self.project, user=self.student)
        Supervision.objects.create(
            teacher=self.teacher, student=self.student, project=self.project
        )
        Notification.objects.create(
            recipient=self.student, message="Feedback ready", url="/writing/"
        )
        AssistantMessage.objects.create(
            project=self.project,
            user=self.student,
            role=AssistantMessage.Role.USER,
            content="Help me outline the introduction",
        )

    def assertPageLoads(self, url, status=200):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status, f"GET {url} failed")

    def test_public_pages(self):
        self.assertPageLoads(reverse("login"))
        self.assertPageLoads(reverse("register"))
        self.assertPageLoads(reverse("password_reset"))

    def test_student_pages(self):
        self.client.force_login(self.student)
        self.assertPageLoads(reverse("student_dashboard"))
        self.assertPageLoads(reverse("research:project_list"))
        self.assertPageLoads(reverse("research:project_create"))
        self.assertPageLoads(reverse("research:project_detail", args=[self.project.pk]))
        self.assertPageLoads(reverse("research:chapter_create", args=[self.project.pk]))
        self.assertPageLoads(reverse("collaboration:index"))
        self.assertPageLoads(reverse("assistant:index"))
        self.assertPageLoads(reverse("assistant:chat", args=[self.project.pk]))
        self.assertPageLoads(reverse("sources:source_list"))
        self.assertPageLoads(reverse("sources:source_create", args=[self.project.pk]))
        self.assertPageLoads(reverse("writing:index"))
        self.assertPageLoads(reverse("writing:chapter_edit", args=[self.chapter.pk]))
        self.assertPageLoads(reverse("citations:citation_list"))
        self.assertPageLoads(reverse("citations:citation_create", args=[self.project.pk]))
        self.assertPageLoads(reverse("notifications:list"))
        self.assertPageLoads(reverse("supervision:list"))

    def test_teacher_pages(self):
        self.client.force_login(self.teacher)
        self.assertPageLoads(reverse("teacher_dashboard"))
        self.assertPageLoads(reverse("teacher_submissions"))
        self.assertPageLoads(reverse("research:project_list"))
        self.assertPageLoads(reverse("writing:index"))
        self.assertPageLoads(reverse("analytics:dashboard"))
        self.assertPageLoads(reverse("notifications:list"))

    def test_admin_pages(self):
        self.client.force_login(self.admin)
        self.assertPageLoads(reverse("admin_dashboard"))
        self.assertPageLoads(reverse("research:project_list"))
        self.assertPageLoads(reverse("analytics:dashboard"))
        self.assertPageLoads(reverse("notifications:list"))

    def test_list_filters_and_pagination(self):
        self.client.force_login(self.student)
        self.assertPageLoads(reverse("research:project_list") + "?q=memory&sort=title")
        self.assertPageLoads(
            reverse("research:project_list") + "?status=IN_PROGRESS&sort=deadline"
        )
        self.assertPageLoads(reverse("sources:source_list") + "?q=sleep&type=JOURNAL")
        self.assertPageLoads(reverse("citations:citation_list") + "?q=sleep")
        self.assertPageLoads(reverse("writing:index") + "?q=introduction&status=DRAFT")
        self.assertPageLoads(reverse("notifications:list") + "?filter=unread")

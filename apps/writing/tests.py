from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.collaboration.models import ProjectMembership
from apps.notifications.models import Notification
from apps.research.models import Chapter, Project

from .models import ChapterDraft, ChapterReview


class SubmitForReviewTests(TestCase):
    def test_submitting_a_draft_notifies_the_adviser(self):
        student = User.objects.create_user(
            "student", password="pass12345", role="STUDENT"
        )
        teacher = User.objects.create_user(
            "teacher", password="pass12345", role="TEACHER"
        )
        project = Project.objects.create(
            title="P", owner=student, adviser=teacher
        )
        chapter = Chapter.objects.create(
            project=project, number=1, title="Introduction"
        )

        self.client.force_login(student)
        response = self.client.post(
            reverse("writing:chapter_edit", args=[chapter.pk]),
            {"content": "Draft text", "action": "submit"},
        )

        self.assertEqual(response.status_code, 302)
        chapter.refresh_from_db()
        self.assertEqual(chapter.status, Chapter.Status.FOR_REVIEW)
        draft = chapter.drafts.first()
        self.assertIsNotNone(draft.submitted_at)
        notification = teacher.notifications.get()
        self.assertIn("submitted", notification.message)
        self.assertEqual(
            notification.url,
            reverse("teacher_submissions") + f"?chapter={chapter.pk}",
        )


class TeacherReviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            "revstudent", password="pass12345", role="STUDENT"
        )
        cls.teacher = User.objects.create_user(
            "revteacher", password="pass12345", role="TEACHER"
        )
        cls.other_teacher = User.objects.create_user(
            "otherteacher", password="pass12345", role="TEACHER"
        )
        cls.project = Project.objects.create(
            title="Review project", owner=cls.student, adviser=cls.teacher
        )
        cls.chapter = Chapter.objects.create(
            project=cls.project,
            number=1,
            title="Introduction",
            status=Chapter.Status.FOR_REVIEW,
        )
        cls.draft = ChapterDraft.objects.create(
            chapter=cls.chapter,
            author=cls.student,
            content="Submitted text",
            is_submitted=True,
        )

    def test_review_page_renders_for_adviser(self):
        self.client.force_login(self.teacher)
        response = self.client.get(
            reverse("teacher_submissions"), {"chapter": self.chapter.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submitted text")

    def test_approve_marks_chapter_and_notifies_owner(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("teacher_submissions"),
            {
                "chapter": self.chapter.pk,
                "decision": "APPROVED",
                "feedback": "Looks good",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.APPROVED)
        self.assertTrue(
            ChapterReview.objects.filter(
                chapter=self.chapter, decision=ChapterReview.Decision.APPROVED
            ).exists()
        )
        notification = self.student.notifications.get()
        self.assertIn("approved", notification.message)
        self.assertEqual(
            notification.url,
            reverse("writing:chapter_edit", args=[self.chapter.pk]),
        )

    def test_request_revision_marks_chapter_revision(self):
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("teacher_submissions"),
            {
                "chapter": self.chapter.pk,
                "decision": "REVISION",
                "feedback": "Add citations",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.REVISION)

    def test_non_adviser_cannot_review(self):
        self.client.force_login(self.other_teacher)
        response = self.client.post(
            reverse("teacher_submissions"),
            {"chapter": self.chapter.pk, "decision": "APPROVED"},
        )
        self.assertEqual(response.status_code, 404)

    def test_review_requires_for_review_status(self):
        self.chapter.status = Chapter.Status.DRAFT
        self.chapter.save(update_fields=["status"])
        self.client.force_login(self.teacher)
        response = self.client.post(
            reverse("teacher_submissions"),
            {"chapter": self.chapter.pk, "decision": "APPROVED"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ChapterReview.objects.count(), 0)


class StudentRevisionWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            "student", password="pass12345", role="STUDENT"
        )
        cls.other_student = User.objects.create_user(
            "otherstudent", password="pass12345", role="STUDENT"
        )
        cls.teacher = User.objects.create_user(
            "teacher", password="pass12345", role="TEACHER"
        )
        cls.other_teacher = User.objects.create_user(
            "otherteacher2", password="pass12345", role="TEACHER"
        )
        cls.project = Project.objects.create(
            title="Thesis", owner=cls.student, adviser=cls.teacher
        )
        cls.chapter = Chapter.objects.create(
            project=cls.project,
            number=1,
            title="Introduction",
            status=Chapter.Status.REVISION,
        )
        cls.draft = ChapterDraft.objects.create(
            chapter=cls.chapter,
            author=cls.student,
            content="Original text",
            is_submitted=True,
        )
        cls.review = ChapterReview.objects.create(
            chapter=cls.chapter,
            reviewer=cls.teacher,
            decision=ChapterReview.Decision.REVISION,
            feedback="Add citations.",
        )
        ProjectMembership.objects.create(
            project=cls.project, user=cls.other_student
        )

    def _url(self):
        return reverse("writing:chapter_edit", args=[self.chapter.pk])

    def test_student_can_open_revision_chapter(self):
        self.client.force_login(self.student)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)

    def test_student_sees_teacher_feedback(self):
        self.client.force_login(self.student)
        response = self.client.get(self._url())
        self.assertContains(response, "Add citations.")

    def test_student_dashboard_shows_revision_indicator(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("student_dashboard"))
        self.assertContains(response, "Revision required")

    def test_student_can_save_returned_chapter(self):
        self.client.force_login(self.student)
        response = self.client.post(
            self._url(), {"content": "Revised text", "action": "save"}
        )
        self.assertEqual(response.status_code, 302)
        self.draft.refresh_from_db()
        self.chapter.refresh_from_db()
        self.assertEqual(self.draft.content, "Revised text")
        self.assertFalse(self.draft.is_submitted)
        self.assertEqual(self.chapter.status, Chapter.Status.REVISION)

    def test_resubmission_changes_status_and_records_timestamp(self):
        self.client.force_login(self.student)
        response = self.client.post(
            self._url(), {"content": "Revised text", "action": "submit"}
        )
        self.assertEqual(response.status_code, 302)
        self.chapter.refresh_from_db()
        self.draft.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.FOR_REVIEW)
        self.assertTrue(self.draft.is_submitted)
        self.assertIsNotNone(self.draft.submitted_at)

    def test_resubmission_notifies_adviser_with_correct_link(self):
        self.client.force_login(self.student)
        self.client.post(
            self._url(), {"content": "Revised text", "action": "submit"}
        )
        notification = self.teacher.notifications.get()
        self.assertIn("resubmitted", notification.message)
        self.assertEqual(
            notification.url,
            reverse("teacher_submissions") + f"?chapter={self.chapter.pk}",
        )

    def test_previous_reviews_remain_intact(self):
        self.client.force_login(self.student)
        self.client.post(
            self._url(), {"content": "Revised text", "action": "save"}
        )
        self.assertEqual(self.chapter.reviews.count(), 1)
        self.review.refresh_from_db()
        self.assertEqual(self.review.feedback, "Add citations.")

    def test_another_student_cannot_edit_chapter(self):
        self.client.force_login(self.other_student)
        response = self.client.post(
            self._url(), {"content": "Hijack", "action": "save"}
        )
        self.assertEqual(response.status_code, 403)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.content, "Original text")

    def test_student_cannot_approve_chapter(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("teacher_submissions"),
            {"chapter": self.chapter.pk, "decision": "APPROVED"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ChapterReview.objects.count(), 1)

    def test_student_cannot_edit_approved_chapter(self):
        self.chapter.status = Chapter.Status.APPROVED
        self.chapter.save(update_fields=["status"])
        self.client.force_login(self.student)
        response = self.client.post(
            self._url(), {"content": "Change", "action": "save"}
        )
        self.assertEqual(response.status_code, 403)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.content, "Original text")

    def test_teacher_can_review_resubmitted_chapter(self):
        self.client.force_login(self.student)
        self.client.post(
            self._url(), {"content": "Revised text", "action": "submit"}
        )

        self.client.force_login(self.teacher)
        listing = self.client.get(reverse("teacher_submissions"))
        self.assertContains(listing, "Introduction")

        response = self.client.post(
            reverse("teacher_submissions"),
            {
                "chapter": self.chapter.pk,
                "decision": "APPROVED",
                "feedback": "Great work",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.APPROVED)
        self.assertEqual(self.chapter.reviews.count(), 2)

    def test_teacher_cannot_open_other_advisers_submission(self):
        self.client.force_login(self.other_teacher)
        response = self.client.get(
            reverse("teacher_submissions"), {"chapter": self.chapter.pk}
        )
        self.assertEqual(response.status_code, 404)

    def test_repeated_submission_does_not_create_duplicates(self):
        self.client.force_login(self.student)
        self.client.post(
            self._url(), {"content": "Revised text", "action": "submit"}
        )
        self.client.post(
            self._url(), {"content": "Revised text", "action": "submit"}
        )
        self.assertEqual(self.chapter.drafts.count(), 1)
        self.assertEqual(self.teacher.notifications.count(), 1)
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.FOR_REVIEW)

    def test_empty_resubmission_is_rejected(self):
        self.client.force_login(self.student)
        response = self.client.post(
            self._url(), {"content": "   ", "action": "submit"}
        )
        self.assertEqual(response.status_code, 200)
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.REVISION)
        self.assertEqual(self.teacher.notifications.count(), 0)

    def test_revision_notification_includes_feedback_and_chapter_link(self):
        self.chapter.status = Chapter.Status.FOR_REVIEW
        self.chapter.save(update_fields=["status"])
        self.client.force_login(self.teacher)
        self.client.post(
            reverse("teacher_submissions"),
            {
                "chapter": self.chapter.pk,
                "decision": "REVISION",
                "feedback": "Fix the methodology section",
            },
        )
        notification = self.student.notifications.get()
        self.assertIn("Fix the methodology section", notification.message)
        self.assertEqual(
            notification.url,
            reverse("writing:chapter_edit", args=[self.chapter.pk]),
        )

    def test_full_cycle_preserves_review_history(self):
        self.client.force_login(self.student)
        self.client.post(
            self._url(), {"content": "Revised text", "action": "submit"}
        )
        self.client.force_login(self.teacher)
        self.client.post(
            reverse("teacher_submissions"),
            {
                "chapter": self.chapter.pk,
                "decision": "APPROVED",
                "feedback": "Approved after revision",
            },
        )
        self.chapter.refresh_from_db()
        self.assertEqual(self.chapter.status, Chapter.Status.APPROVED)
        decisions = list(
            self.chapter.reviews.order_by("created_at").values_list(
                "decision", flat=True
            )
        )
        self.assertEqual(decisions, ["REVISION", "APPROVED"])

    def test_csrf_protection_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        response = client.post(
            self._url(), {"content": "No token", "action": "save"}
        )
        self.assertEqual(response.status_code, 403)

from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from apps.accounts.models import User
from apps.research.models import Project
from apps.sources.models import Source

from .formatting import format_apa, format_mla
from .models import Citation


class FormattingTests(SimpleTestCase):
    def test_apa_book(self):
        source = SimpleNamespace(
            authors="Dela Cruz, J.",
            year=2020,
            title="Research Methods",
            source_type=Source.SourceType.BOOK,
            publisher="Acme Press",
            url="",
            doi="",
        )
        self.assertEqual(
            format_apa(source), "Dela Cruz, J. (2020). Research Methods. Acme Press."
        )

    def test_mla_website_without_year(self):
        source = SimpleNamespace(
            authors="Santos, M.",
            year=None,
            title="How to Research",
            source_type=Source.SourceType.WEBSITE,
            publisher="",
            url="https://example.com",
            doi="",
        )
        self.assertEqual(
            format_mla(source),
            'Santos, M. "How to Research." n.d. https://example.com.',
        )


class CitationModelTests(TestCase):
    def test_formatted_text_is_computed_on_save(self):
        user = User.objects.create_user(
            "writer", password="pass12345", role="STUDENT"
        )
        project = Project.objects.create(title="P", owner=user)
        source = Source.objects.create(
            project=project,
            title="A Study",
            authors="Reyes, M.",
            year=2021,
            publisher="Pub Co",
        )
        citation = Citation.objects.create(
            project=project, source=source, style=Citation.Style.APA
        )
        self.assertIn("Reyes, M. (2021). A Study.", citation.formatted_text)

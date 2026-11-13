import os
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from .services import ask_assistant


class AssistantFallbackTests(SimpleTestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_missing_api_key_returns_configuration_message(self):
        project = SimpleNamespace(title="Paper", abstract="")
        reply = ask_assistant(project, [], "Hello")
        self.assertIn("not configured", reply)

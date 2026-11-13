"""Test settings: run the suite against in-memory SQLite.

The development MySQL user may not be allowed to create `test_*` databases,
so tests use an isolated in-memory database instead.

Usage: python manage.py test --settings=config.settings_test
"""

from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

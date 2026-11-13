from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("research/", include("apps.research.urls")),
    path("writing/", include("apps.writing.urls")),
    path("sources/", include("apps.sources.urls")),
    path("citations/", include("apps.citations.urls")),
    path("collaboration/", include("apps.collaboration.urls")),
    path("supervision/", include("apps.supervision.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("assistant/", include("apps.assistant.urls")),
]

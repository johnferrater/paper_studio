from django.urls import path

from . import views

app_name = "citations"

urlpatterns = [
    path("", views.CitationListView.as_view(), name="citation_list"),
    path(
        "project/<int:project_pk>/new/",
        views.citation_create,
        name="citation_create",
    ),
]

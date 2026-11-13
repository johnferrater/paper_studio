from django.urls import path

from . import views

app_name = "sources"

urlpatterns = [
    path("", views.SourceListView.as_view(), name="source_list"),
    path(
        "project/<int:project_pk>/new/",
        views.source_create,
        name="source_create",
    ),
]

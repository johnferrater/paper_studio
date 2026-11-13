from django.urls import path

from . import views

app_name = "research"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="project_list"),
    path("new/", views.ProjectCreateView.as_view(), name="project_create"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path(
        "<int:project_pk>/chapters/new/",
        views.ChapterCreateView.as_view(),
        name="chapter_create",
    ),
]

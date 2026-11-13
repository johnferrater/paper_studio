from django.urls import path

from . import views

app_name = "collaboration"

urlpatterns = [
    path("", views.CollaborationIndexView.as_view(), name="index"),
    path("project/<int:project_pk>/join/", views.join, name="join"),
    path("project/<int:project_pk>/leave/", views.leave, name="leave"),
]

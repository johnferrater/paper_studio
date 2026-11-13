from django.urls import path

from . import views

app_name = "writing"

urlpatterns = [
    path("", views.WritingIndexView.as_view(), name="index"),
    path("chapter/<int:pk>/", views.chapter_edit, name="chapter_edit"),
]

from django.urls import path

from . import views

app_name = "assistant"

urlpatterns = [
    path("", views.AssistantIndexView.as_view(), name="index"),
    path("project/<int:project_pk>/", views.chat, name="chat"),
]

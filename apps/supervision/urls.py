from django.urls import path

from . import views

app_name = "supervision"

urlpatterns = [
    path("", views.SupervisionListView.as_view(), name="list"),
]

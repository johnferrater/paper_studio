from django import forms

from apps.core.forms import StyledModelForm

from .models import Chapter, Project


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ("title", "abstract", "deadline")
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}


class ChapterForm(StyledModelForm):
    class Meta:
        model = Chapter
        fields = ("number", "title", "status")

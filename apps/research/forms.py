from django import forms

from .models import Chapter, Project


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if widget.__class__.__name__ == "Textarea":
                widget.attrs.setdefault("class", "textarea")
            else:
                widget.attrs.setdefault("class", "input")


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ("title", "abstract", "deadline")
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}


class ChapterForm(StyledModelForm):
    class Meta:
        model = Chapter
        fields = ("number", "title", "status")

from django import forms

from apps.core.forms import StyledModelForm

from .models import Citation


class CitationForm(StyledModelForm):
    class Meta:
        model = Citation
        fields = ("source", "style")

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project is not None:
            self.fields["source"].queryset = project.sources.all()

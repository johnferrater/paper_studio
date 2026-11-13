from django import forms

from .models import Citation


class CitationForm(forms.ModelForm):
    class Meta:
        model = Citation
        fields = ("source", "style")

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if project is not None:
            self.fields["source"].queryset = project.sources.all()
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "input")

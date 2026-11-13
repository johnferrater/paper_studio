from django import forms

from .models import Source


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = (
            "title",
            "authors",
            "year",
            "source_type",
            "publisher",
            "url",
            "doi",
            "notes",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__.__name__ == "Textarea":
                field.widget.attrs.setdefault("class", "textarea")
            else:
                field.widget.attrs.setdefault("class", "input")

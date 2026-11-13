from django import forms

from apps.core.forms import StyledModelForm

from .models import Source


class SourceForm(StyledModelForm):
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

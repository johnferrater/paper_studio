from django import forms

from .models import ChapterDraft


class ChapterDraftForm(forms.ModelForm):
    class Meta:
        model = ChapterDraft
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "rows": 16,
                    "placeholder": "Write your chapter here…",
                    "data-word-count": "word-count",
                }
            )
        }

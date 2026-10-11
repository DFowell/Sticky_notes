from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    """Form used for both creating and editing a note."""

    class Meta:
        model = Note
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Note title"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Write your note here...",
                }
            ),
        }

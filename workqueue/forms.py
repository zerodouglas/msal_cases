from django import forms
from django.utils import timezone
from .models import Case

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ["title", "description", "severity", "going_to_da", "da_due_at"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "usa-input"}),
            "description": forms.Textarea(attrs={"class": "usa-textarea", "rows": 4}),
            "severity": forms.Select(attrs={"class": "usa-select"}),
            "going_to_da": forms.CheckboxInput(attrs={"class": "usa-checkbox__input"}),
            "da_due_at": forms.DateTimeInput(
                attrs={"class": "usa-input", "type": "datetime-local"}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        going = cleaned.get("going_to_da")
        da_due_at = cleaned.get("da_due_at")
        if going and not da_due_at:
            self.add_error("da_due_at", "DA-bound cases require a DA due date.")
        if da_due_at and da_due_at < timezone.now():
            self.add_error("da_due_at", "DA due date must be in the future.")
        return cleaned

from django import forms
from django.forms.widgets import DateInput
from django.utils import timezone

from tasks import models


class CreateUpdateTask(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = [
            "title",
            "description",
            "priority",
            "due_date",
            "assigned_to",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "due_date": DateInput(attrs={"class": "form-control", "type": "date"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.SelectMultiple(
                attrs={"class": "form-select", "multiple": "multiple"}
            ),
        }

    def __init__(self, *args, **kwargs):
        readonly_fields = kwargs.pop("readonly_fields", [])
        super(CreateUpdateTask, self).__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields["due_date"].widget.attrs.update({"min": today})

        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs["readonly"] = "readonly"


class SubmitTaskForm(forms.Form):
    remarks = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "Remarks"}
        )
    )

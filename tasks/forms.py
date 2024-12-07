from django import forms
from django.forms.widgets import DateInput
from django.utils import timezone

from . import models


class CreateUpdateTask(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = [
            "title",
            "description",
            "type",
            "priority",
            "due_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "due_date": DateInput(attrs={"class": "form-control", "type": "date"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
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

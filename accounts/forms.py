from django import forms


class UserLoginForm(forms.Form):
    login_username = forms.CharField(
        max_length=75, widget=forms.TextInput(attrs={"placeholder": "Username"})
    )
    login_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

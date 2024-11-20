from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_superuser']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_staff:
            self.fields.pop('is_staff')
            self.fields.pop('is_superuser')
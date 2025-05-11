from django import forms
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

from .models import Research, ResearchFile, Route
from .models import Defect
from .models import News, ForumMessage

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label="Логин или Email", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

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

class ResearchForm(forms.ModelForm):
    class Meta:
        model = Research
        fields = ['title', 'description', 'image', 'kml_file']

class ResearchFileForm(forms.ModelForm):
    class Meta:
        model = ResearchFile
        fields = ['file', 'description']


class DefectForm(forms.ModelForm):
    class Meta:
        model = Defect
        fields = ['defect_name', 'defect_description', 'defect_date', 'defect_coordinates', 'defect_type']
        widgets = {
            'defect_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_defect_coordinates(self):
        coordinates = self.cleaned_data.get('defect_coordinates')
        try:
            lat, lon = map(str.strip, coordinates.split(','))
            float(lat)  # Проверяем что это числа
            float(lon)
            return coordinates
        except (ValueError, AttributeError):
            raise forms.ValidationError('Введите координаты в формате "широта, долгота" (числовые значения)')

class XMLUploadForm(forms.Form):
    xml_file = forms.FileField(
        label='XML файл',
        help_text='Загрузите XML файл с данными исследования',
        validators=[FileExtensionValidator(allowed_extensions=['xml'])]
    )

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['kml_file']
        widgets = {
            'kml_file': forms.FileInput(attrs={
                'accept': '.kml',
                'class': 'form-control'
            })
        }
        labels = {
            'kml_file': 'KML файл с маршрутом'
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Пересчитываем расстояние после сохранения
            instance.distance = instance.calculate_distance()
            instance.save()
        return instance

class ForumMessageForm(forms.ModelForm):
    class Meta:
        model = ForumMessage
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
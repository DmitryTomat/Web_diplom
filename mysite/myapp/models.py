from django.utils import timezone

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

class Research(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='researches')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='research_images/', blank=True, null=True)
    kml_file = models.FileField(upload_to='research_kml_files/', blank=True, null=True)

    def __str__(self):
        return self.title

class ResearchFile(models.Model):
    research = models.ForeignKey(Research, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='research_files/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.research.title}"

class Defect(models.Model):
    research = models.ForeignKey(Research, on_delete=models.CASCADE, related_name='defects')
    defect_date = models.DateTimeField(default=timezone.now)
    defect_name = models.CharField(max_length=255)
    defect_description = models.TextField()
    defect_coordinates = models.CharField(max_length=255)
    defect_type = models.CharField(max_length=255)  # Добавляем поле для типа дефекта

    def clean(self):
        super().clean()
        # Проверяем формат координат
        try:
            parts = self.defect_coordinates.split(',')
            if len(parts) != 2:
                raise ValidationError('Координаты должны быть в формате "широта, долгота"')
            float(parts[0].strip())  # Проверяем, что широта - число
            float(parts[1].strip())  # Проверяем, что долгота - число
        except ValueError:
            raise ValidationError('Координаты должны быть числовыми значениями')

    @classmethod
    def create_from_xml(cls, research, defect_data):
        """Создает дефект из данных XML"""
        return cls.objects.create(
            research=research,
            defect_date=timezone.now(),
            defect_name=defect_data.get('defect_name', 'Неизвестный дефект'),
            defect_description=defect_data.get('defect_description', ''),
            defect_coordinates=defect_data.get('defect_coordinates', '0, 0'),
            defect_type=defect_data.get('defect_type', 'Неизвестный тип')
        )

    def __str__(self):
        return f"{self.defect_name} - {self.research.title}"

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)  # Добавляем поле для фотографии

    def __str__(self):
        return self.title
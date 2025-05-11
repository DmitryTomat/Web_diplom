from django.utils import timezone

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from math import radians, sin, cos, sqrt, atan2

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


class Route(models.Model):
    research = models.ForeignKey(Research, on_delete=models.CASCADE, related_name='routes')
    kml_file = models.FileField(upload_to='research_routes/')
    created_at = models.DateTimeField(auto_now_add=True)
    coordinates = models.TextField(blank=True, null=True)
    distance = models.FloatField(default=0, verbose_name="Расстояние (м)", null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # При сохранении парсим KML файл и извлекаем координаты
        if self.kml_file:
            self.parse_kml_and_save_coordinates()

    def parse_kml_and_save_coordinates(self):
        try:
            import xml.etree.ElementTree as ET
            from django.core.files.base import ContentFile
            kml_content = self.kml_file.read().decode('utf-8')
            root = ET.fromstring(kml_content)

            # Ищем координаты в KML файле
            coordinates = []
            for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
                linestring = placemark.find('{http://www.opengis.net/kml/2.2}LineString')
                if linestring is not None:
                    coords = linestring.find('{http://www.opengis.net/kml/2.2}coordinates')
                    if coords is not None and coords.text:
                        coordinates = coords.text.strip().split()

            # Сохраняем координаты в формате "lon,lat;lon,lat;..."
            if coordinates:
                self.coordinates = ';'.join([','.join(coord.split(',')[:2]) for coord in coordinates])
                super().save(update_fields=['coordinates'])

                # Рассчитываем и сохраняем расстояние
                self.distance = self.calculate_distance()
                super().save(update_fields=['distance'])
        except Exception as e:
            print(f"Error parsing KML: {e}")

    def __str__(self):
        return f"Route for {self.research.title}"

    def calculate_distance(self):
        """
        Рассчитывает общее расстояние маршрута в километрах (используя формулу гаверсинусов)
        """
        if not self.coordinates:
            return 0.0

        total_distance = 0.0
        coords = self.coordinates.split(';')

        for i in range(len(coords)-1):
            try:
                lon1, lat1 = map(float, coords[i].split(','))
                lon2, lat2 = map(float, coords[i+1].split(','))

                # Формула гаверсинусов для расчета расстояния между двумя точками на сфере
                R = 6371.0  # Радиус Земли в км

                lat1_rad = radians(lat1)
                lon1_rad = radians(lon1)
                lat2_rad = radians(lat2)
                lon2_rad = radians(lon2)

                dlon = lon2_rad - lon1_rad
                dlat = lat2_rad - lat1_rad

                a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))

                distance = R * c
                total_distance += distance

            except (ValueError, IndexError):
                continue

        return round(total_distance, 2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # При сохранении рассчитываем и сохраняем расстояние
        if self.kml_file:
            self.parse_kml_and_save_coordinates()
            self.distance = self.calculate_distance()
            super().save(update_fields=['distance'])


class ForumMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"

    def get_replies(self):
        return ForumMessage.objects.filter(parent_message=self).order_by('created_at')

    def can_delete(self, user):
        return user.is_staff or user == self.user

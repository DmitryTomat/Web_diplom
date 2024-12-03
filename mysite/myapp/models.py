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
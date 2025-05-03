from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Research, Defect

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                 'is_staff', 'is_active', 'date_joined', 'last_login')

class ResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ('id', 'title', 'description', 'created_at', 'image', 'kml_file')

class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = ('id', 'defect_name', 'defect_description',
                 'defect_coordinates', 'defect_type', 'defect_date')
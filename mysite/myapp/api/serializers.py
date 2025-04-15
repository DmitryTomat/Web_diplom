from rest_framework import serializers
from ..models import Research, Defect, News

class ResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['id', 'title', 'description', 'created_at']

class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = ['id', 'defect_name', 'defect_description', 'defect_coordinates']

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'created_at']
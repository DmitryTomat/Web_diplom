from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import ResearchSerializer, DefectSerializer, NewsSerializer
from ..models import Research, Defect, News
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Неверные данные"}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_researches(request):
    researches = Research.objects.filter(user=request.user)
    serializer = ResearchSerializer(researches, many=True)
    return Response(serializer.data)
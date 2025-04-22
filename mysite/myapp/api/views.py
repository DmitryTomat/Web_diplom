from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Проверка учетных данных через стандартную систему аутентификации Django
    user = authenticate(username=username, password=password)

    if user:
        # Создаем или получаем токен пользователя
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'status': 'success',
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response({
            'status': 'error',
            'message': 'Invalid credentials'
        }, status=400)
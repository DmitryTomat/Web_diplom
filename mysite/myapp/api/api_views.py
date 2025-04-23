from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def api_login(request):
    logger.info("API_LOGIN FUNCTION IS BEING CALLED!")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            logger.info(f"Authenticating user: {username}")
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Создаем простой токен (в реальном приложении используйте JWT)
                from django.contrib.auth import login
                from django.contrib.sessions.models import Session
                
                # Создаем сессию для пользователя
                login(request, user)
                
                # Генерируем простой токен на основе сессии
                token = request.session.session_key
                
                logger.info(f"User {username} authenticated successfully")
                return JsonResponse({
                    'status': 'success',
                    'token': token,
                    'username': user.username
                })
            else:
                logger.warning(f"Invalid credentials for user: {username}")
                return JsonResponse({
                    'status': 'error',
                    'error': 'Invalid credentials'
                }, status=401)
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'error': 'Method not allowed'
    }, status=405)
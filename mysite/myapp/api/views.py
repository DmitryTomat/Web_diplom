from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                return JsonResponse({
                    'status': 'success',
                    'token': 'dummy_token',  # В реальном приложении используйте JWT или другой механизм
                    'username': user.username
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Invalid credentials'
                }, status=401)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'error': 'Method not allowed'
    }, status=405)
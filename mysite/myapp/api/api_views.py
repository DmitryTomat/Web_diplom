from django.http import JsonResponse
from django.contrib.auth import authenticate
import logging
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.core.exceptions import PermissionDenied
from ..models import Research, Defect
from django.db.models import Count

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


@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
            confirm_password = data.get('confirm_password')

            # Валидация данных
            if not username or not password or not confirm_password:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Все обязательные поля должны быть заполнены'
                }, status=400)

            if password != confirm_password:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Пароли не совпадают'
                }, status=400)

            if len(password) < 8:
                return JsonResponse({
                    'status': 'error',
                    'error': 'Пароль должен содержать минимум 8 символов'
                }, status=400)

            User = get_user_model()
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'error': 'Пользователь с таким логином уже существует'
                }, status=400)

            # Создание пользователя
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )

            return JsonResponse({
                'status': 'success',
                'user_id': user.id,
                'username': user.username
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'error': 'Method not allowed'
    }, status=405)


@require_GET
@login_required
def api_profile(request):
    try:
        logger.info(f"Запрос профиля от пользователя: {request.user.username}")
        print(f"Запрос профиля от пользователя: {request.user.username}")
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_staff': user.is_staff,
            'profile_photo': request.build_absolute_uri(user.profile_photo.url) if user.profile_photo else None
        }
    except Exception as e:
        logger.error(f"Ошибка при загрузке профиля: {str(e)}")
        return JsonResponse(data)


@require_GET
@login_required
def api_users(request):
    """Получение списка пользователей (только для администраторов)"""
    if not request.user.is_staff:
        raise PermissionDenied("Только администраторы могут просматривать список пользователей")

    users = get_user_model().objects.all().order_by('id')
    data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'date_joined': user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else None,
        'last_login': user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
    } for user in users]
    return JsonResponse(data, safe=False)

@require_GET
@login_required
def api_researches(request):
    """Получение списка исследований текущего пользователя"""
    researches = Research.objects.filter(user=request.user).annotate(
        defect_count=Count('defect')
    ).order_by('-created_at')

    data = [{
        'id': research.id,
        'title': research.title,
        'description': research.description,
        'created_at': research.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'defect_count': research.defect_count,
        'image': request.build_absolute_uri(research.image.url) if research.image else None,
        'kml_file': request.build_absolute_uri(research.kml_file.url) if research.kml_file else None
    } for research in researches]
    return JsonResponse(data, safe=False)


@require_GET
@login_required
def api_research_detail(request, research_id):
    """Получение детальной информации об исследовании"""
    research = get_object_or_404(Research, id=research_id, user=request.user)
    defects = Defect.objects.filter(research=research)

    data = {
        'id': research.id,
        'title': research.title,
        'description': research.description,
        'created_at': research.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'image': request.build_absolute_uri(research.image.url) if research.image else None,
        'kml_file': request.build_absolute_uri(research.kml_file.url) if research.kml_file else None,
        'defect_count': defects.count(),
        'defects': [{
            'id': defect.id,
            'defect_name': defect.defect_name,
            'defect_description': defect.defect_description,
            'defect_coordinates': defect.defect_coordinates,
            'defect_type': defect.defect_type,
            'defect_date': defect.defect_date.strftime("%Y-%m-%d %H:%M:%S") if defect.defect_date else None
        } for defect in defects]
    }
    return JsonResponse(data)


@require_GET
@login_required
def api_user_detail(request, user_id):
    """Получение детальной информации о пользователе"""
    if not request.user.is_staff:
        raise PermissionDenied("Только администраторы могут просматривать данные пользователей")

    user = get_object_or_404(get_user_model(), id=user_id)
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'date_joined': user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else None,
        'last_login': user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None,
        'profile_photo': request.build_absolute_uri(user.profile_photo.url) if user.profile_photo else None
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def api_update_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)
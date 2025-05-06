from datetime import timezone

import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.contrib.auth import authenticate
import logging
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from ..models import Research, Defect, ResearchFile

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


@csrf_exempt
def api_profile(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'error': 'Only GET method allowed'}, status=405)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

    token = auth_header.split(' ')[1].strip()

    try:
        session = Session.objects.get(session_key=token)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        profile_data = {
            'status': 'success',
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'is_staff': user.is_staff
        }

        # Удаляем проверку profile_photo, так как её нет в стандартной модели User
        return JsonResponse(profile_data)

    except Session.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Session expired or invalid'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


@csrf_exempt
def api_update_profile(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Only POST method allowed'}, status=405)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

    token = auth_header.split(' ')[1].strip()

    try:
        session = Session.objects.get(session_key=token)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        data = json.loads(request.body)

        # Обновляем только те поля, которые пришли в запросе
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']

        user.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully'
        })

    except Session.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Session expired or invalid'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)


@csrf_exempt
def api_research_list(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'error': 'Only GET method allowed'}, status=405)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

    token = auth_header.split(' ')[1].strip()

    try:
        session = Session.objects.get(session_key=token)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        researches = Research.objects.filter(user=user)
        research_list = []

        for research in researches:
            research_list.append({
                'id': research.id,
                'title': research.title,
                'description': research.description,
                'created_at': research.created_at.strftime("%d.%m.%Y %H:%M"),
                'image_url': research.image.url if research.image else None,
                'kml_file_url': research.kml_file.url if research.kml_file else None
            })

        return JsonResponse({
            'status': 'success',
            'researches': research_list
        })

    except Session.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Session expired or invalid'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


# myapp/api/api_views.py
@csrf_exempt
def api_research_detail(request, research_id):
    if request.method == 'GET':
        # Получение деталей исследования
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

        token = auth_header.split(' ')[1].strip()

        try:
            session = Session.objects.get(session_key=token)
            user_id = session.get_decoded().get('_auth_user_id')
            user = User.objects.get(id=user_id)

            research = Research.objects.get(id=research_id, user=user)
            files = ResearchFile.objects.filter(research=research)
            defects = Defect.objects.filter(research=research)

            research_data = {
                'id': research.id,
                'title': research.title,
                'description': research.description,
                'created_at': research.created_at.strftime("%d.%m.%Y %H:%M"),
                'files': [{
                    'id': file.id,
                    'name': file.file.name,
                    'url': file.file.url,
                    'description': file.description or ''
                } for file in files],
                'defects': [{
                    'id': defect.id,
                    'name': defect.defect_name,
                    'description': defect.defect_description,
                    'date': defect.defect_date.strftime("%d.%m.%Y %H:%M"),
                    'coordinates': defect.defect_coordinates,
                    'type': defect.defect_type
                } for defect in defects]
            }

            return JsonResponse({
                'status': 'success',
                'research': research_data
            })

        except Research.DoesNotExist:
            return JsonResponse({'status': 'error', 'error': 'Research not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        # Удаление исследования
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Token '):
            return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

        token = auth_header.split(' ')[1].strip()

        try:
            session = Session.objects.get(session_key=token)
            user_id = session.get_decoded().get('_auth_user_id')
            user = User.objects.get(id=user_id)

            research = Research.objects.get(id=research_id, user=user)
            research.delete()

            return JsonResponse({
                'status': 'success',
                'message': 'Research deleted successfully'
            })

        except Research.DoesNotExist:
            return JsonResponse({'status': 'error', 'error': 'Research not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_delete_defect(request, defect_id):
    if request.method != 'DELETE':
        return JsonResponse({'status': 'error', 'error': 'Method not allowed'}, status=405)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

    token = auth_header.split(' ')[1].strip()

    try:
        session = Session.objects.get(session_key=token)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        defect = Defect.objects.get(id=defect_id, research__user=user)
        defect.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Defect deleted successfully'
        })

    except Defect.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Defect not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


@csrf_exempt
def api_upload_research(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Method not allowed'}, status=405)

    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Token '):
        return JsonResponse({'status': 'error', 'error': 'Auth header missing or invalid'}, status=401)

    token = auth_header.split(' ')[1].strip()

    try:
        session = Session.objects.get(session_key=token)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        kml_content = data.get('kml_content', '')
        xml_content = data.get('xml_content', '')

        if not title or not description:
            return JsonResponse({'status': 'error', 'error': 'Title and description are required'}, status=400)

        # Создаем исследование
        research = Research.objects.create(
            user=user,
            title=title,
            description=description
        )

        # Обрабатываем KML файл
        if kml_content:
            from django.core.files.base import ContentFile
            research.kml_file.save(
                f'research_{research.id}.kml',
                ContentFile(kml_content.encode('utf-8'))
            )
            research.save()

        # Обрабатываем XML с дефектами
        if xml_content:
            parse_xml_defects(xml_content, research)

        return JsonResponse({
            'status': 'success',
            'research_id': research.id,
            'message': 'Research uploaded successfully'
        })

    except Session.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Session expired or invalid'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'User not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in api_upload_research: {str(e)}")
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)


def parse_xml_defects(xml_content, research):
    try:
        # Парсим XML и создаем дефекты
        root = ET.fromstring(xml_content)

        # Находим все дефекты (адаптируйте в зависимости от структуры вашего XML)
        for defect_elem in root.findall('.//Defect'):
            defect_text = defect_elem.find('defectText').text if defect_elem.find('defectText') is not None else ''
            length_defect = defect_elem.find('lengthDefect').text if defect_elem.find(
                'lengthDefect') is not None else ''
            defect_type = defect_elem.find('defectType').text if defect_elem.find('defectType') is not None else ''

            # Координаты могут быть в разных местах в зависимости от структуры XML
            latitude = defect_elem.find('latitude').text if defect_elem.find('latitude') is not None else '0'
            longitude = defect_elem.find('longitude').text if defect_elem.find('longitude') is not None else '0'

            defect = Defect.objects.create(
                research=research,
                defect_name=defect_text,
                defect_description=length_defect,
                defect_type=defect_type,
                defect_coordinates=f"{latitude},{longitude}"
            )

            # Обработка фотографий, если они есть
            for photo_elem in defect_elem.findall('picture'):
                photo_path = photo_elem.text if photo_elem.text else ''
                # Здесь можно добавить обработку загрузки фотографий
                if photo_path:
                    # Логика загрузки фото
                    pass

    except ET.ParseError as e:
        logger.error(f"XML parsing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing XML defects: {str(e)}")

from django.contrib.auth import logout
from .forms import RegistrationForm
from .forms import UserForm
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import ResearchForm, ResearchFileForm, DefectForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import xml.etree.ElementTree as ET
from .forms import XMLUploadForm
from .forms import NewsForm
from .forms import RouteForm, ForumMessageForm, ForumReplyForm
from .models import Research, ResearchFile, Defect, News, Route, ForumMessage  # Добавьте Route в импорты
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Research, Route

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            # Пытаемся найти пользователя по username или email
            if '@' in username_or_email:
                try:
                    user = User.objects.get(email=username_or_email)
                    username = user.username
                except User.DoesNotExist:
                    username = username_or_email
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                # Добавляем ошибку в форму
                form.add_error(None, 'Неправильно введён логин или пароль')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user, request=request)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserForm(instance=request.user, request=request)
    return render(request, 'profile.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def home_view(request):
    return render(request, 'home.html')

def software_view(request):
    return render(request, 'software.html')

def about_view(request):
    return render(request, 'about.html')

def news_view(request):
    return render(request, 'news.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def login_choice_view(request):
    return render(request, 'login_choice.html')

@login_required
def settings_user(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')

        # Обработка загрузки фотографии профиля
        if 'profile_photo' in request.FILES:
            profile_photo = request.FILES['profile_photo']
            path = default_storage.save(f'profile_photos/{user.id}/{profile_photo.name}', ContentFile(profile_photo.read()))
            user.profile_photo = path

        user.save()
        messages.success(request, 'Настройки успешно сохранены.')
        return redirect('settings_user')
    return render(request, 'settings_user.html')

@user_passes_test(lambda u: u.is_staff)
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Пользователь успешно удален.')
    return redirect('user_list')

@user_passes_test(lambda u: u.is_staff)
def toggle_staff_status_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    messages.success(request, 'Роль пользователя успешно изменена.')
    return redirect('user_list')

@login_required
def research_list_view(request, sort_by='title', order='asc'):
    # Определение полей для сортировки
    sort_fields = {
        'title': 'title',
        'date': 'created_at',
    }

    # Определение порядка сортировки
    sort_order = '' if order == 'asc' else '-'

    # Получение отсортированных исследований
    researches = Research.objects.filter(user=request.user).order_by(f'{sort_order}{sort_fields[sort_by]}')

    return render(request, 'research_list.html', {'researches': researches, 'sort_by': sort_by, 'order': order})

@login_required
def create_research_view(request):
    if request.method == 'POST':
        form = ResearchForm(request.POST, request.FILES)
        if form.is_valid():
            research = form.save(commit=False)
            research.user = request.user
            research.save()
            return redirect('research_list')
    else:
        form = ResearchForm()
    return render(request, 'create_research.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def user_research_list_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    researches = Research.objects.filter(user=user)
    return render(request, 'user_research_list.html', {'user': user, 'researches': researches})

@login_required
def upload_file_view(request, research_id):
    if research_id == 0:
        # Создаем новое исследование без данных
        research = Research.objects.create(user=request.user)
        research_id = research.id

    research = get_object_or_404(Research, id=research_id, user=request.user)
    if request.method == 'POST':
        form = ResearchFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.research = research
            file.save()
            return redirect('research_detail', research_id=research.id)
    else:
        form = ResearchFileForm()
    return render(request, 'upload_file.html', {'form': form, 'research': research})

@login_required
def research_detail_view(request, research_id):
    research = get_object_or_404(Research, id=research_id, user=request.user)
    files = ResearchFile.objects.filter(research=research)
    defects = Defect.objects.filter(research=research)  # Получаем дефекты исследования
    return render(request, 'research_detail.html', {'research': research, 'files': files, 'defects': defects})

@login_required
def edit_research_view(request, research_id):
    research = get_object_or_404(Research, id=research_id, user=request.user)
    if request.method == 'POST':
        form = ResearchForm(request.POST, request.FILES, instance=research)
        if form.is_valid():
            form.save()
            return redirect('research_detail', research_id=research.id)
    else:
        form = ResearchForm(instance=research)
    return render(request, 'edit_research.html', {'form': form, 'research': research})

@login_required
def delete_research_view(request, research_id):
    research = get_object_or_404(Research, id=research_id, user=request.user)
    if request.method == 'POST':
        research.delete()
        return redirect('research_list')
    return render(request, 'delete_research.html', {'research': research})

@login_required
def add_defect_view(request, research_id):
    research = get_object_or_404(Research, id=research_id, user=request.user)
    if request.method == 'POST':
        form = DefectForm(request.POST)
        if form.is_valid():
            defect = form.save(commit=False)
            defect.research = research
            defect.save()
            return redirect('research_detail', research_id=research.id)
    else:
        form = DefectForm(initial={'research': research})
    return render(request, 'add_defect.html', {'form': form, 'research': research})

@login_required
def edit_defect(request, defect_id):
    defect = get_object_or_404(Defect, id=defect_id)
    research = defect.research

    # Проверяем, что дефект принадлежит исследованию текущего пользователя
    if research.user != request.user:
        return HttpResponseForbidden("У вас нет прав редактировать этот дефект")

    if request.method == 'POST':
        form = DefectForm(request.POST, instance=defect)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дефект успешно обновлен')
            return redirect('research_detail', research_id=research.id)
    else:
        form = DefectForm(instance=defect)

    return render(request, 'edit_defect.html', {
        'form': form,
        'defect': defect,
        'research': research
    })

@login_required
def delete_defect(request, defect_id):
    defect = get_object_or_404(Defect, id=defect_id)
    research = defect.research

    if research.user != request.user:
        return HttpResponseForbidden("У вас нет прав удалять этот дефект")

    if request.method == 'POST':
        defect.delete()
        messages.success(request, 'Дефект успешно удален')
        return redirect('research_detail', research_id=research.id)

    return render(request, 'confirm_delete_defect.html', {
        'defect': defect,
        'research': research
    })


@login_required
def upload_xml_view(request):
    if request.method == 'POST':
        form = XMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Создаем новое исследование
                research = Research.objects.create(
                    user=request.user,
                    title=root.attrib.get('name', 'Новое исследование'),
                    description='',
                    image=None,
                    kml_file=None
                )

                # Ищем раздел с дефектами
                defects_elem = root.find('.//Дефекты/pictures')
                if defects_elem is not None:
                    for defect_elem in defects_elem:
                        # Получаем координаты из элемента picture
                        picture_elem = defect_elem.find('picture')
                        coordinates = '0, 0'  # Значение по умолчанию
                        if picture_elem is not None:
                            lat = picture_elem.attrib.get('latitude', '0')
                            lon = picture_elem.attrib.get('longitude', '0')
                            coordinates = f"{lat}, {lon}"

                        # Получаем описание дефекта
                        description_elem = defect_elem.find('description')
                        if description_elem is not None:
                            defect_name = description_elem.findtext('defectText', 'Неизвестный дефект')
                            defect_description = description_elem.findtext('lengthDefect', '')
                            defect_type = description_elem.findtext('defectType', 'Неизвестный тип')

                            Defect.objects.create(
                                research=research,
                                defect_date=research.created_at,
                                defect_name=defect_name,
                                defect_description=defect_description,
                                defect_coordinates=coordinates,
                                defect_type=defect_type
                            )

                messages.success(request, 'Файл успешно загружен и обработан.')
                return redirect('research_detail', research_id=research.id)

            except ET.ParseError as e:
                messages.error(request, f'Ошибка парсинга XML: {str(e)}')
            except Exception as e:
                messages.error(request, f'Ошибка обработки файла: {str(e)}')
    else:
        form = XMLUploadForm()
    return render(request, 'upload_xml.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def create_news_view(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)  # Добавляем request.FILES
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('news')
    else:
        form = NewsForm()
    return render(request, 'create_news.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_news_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)  # Добавляем request.FILES
        if form.is_valid():
            form.save()
            return redirect('news')
    else:
        form = NewsForm(instance=news)
    return render(request, 'edit_news.html', {'form': form, 'news': news})

@user_passes_test(lambda u: u.is_staff)
def delete_news_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        news.delete()
        return redirect('news')
    return render(request, 'delete_news.html', {'news': news})

def news_view(request):
    sort_by = request.GET.get('sort_by', '-created_at')  # По умолчанию сортировка по убыванию даты создания
    news_list = News.objects.all().order_by(sort_by)
    return render(request, 'news.html', {'news_list': news_list, 'sort_by': sort_by})

def news_detail_view(request, news_id):
    news = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html', {'news': news})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json


@csrf_exempt  # Отключает CSRF для API (для теста, потом замените на JWT)
def api_login(request):
    if request.method == "POST":
        try:
            # Парсим JSON из тела запроса
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            # Проверяем логин/пароль
            user = authenticate(username=username, password=password)
            if user:
                return JsonResponse({
                    "status": "success",
                    "user_id": user.id,
                    "username": user.username,
                })
            else:
                return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

        return JsonResponse({"status": "test"})

    return JsonResponse({"error": "Only POST allowed"}, status=405)


@login_required
def view_route(request, research_id):
    try:
        research = get_object_or_404(Research, id=research_id, user=request.user)
        route = get_object_or_404(Route, research=research)

        coordinates = []
        if route.coordinates:
            for coord_pair in route.coordinates.split(';'):
                try:
                    lon, lat = coord_pair.split(',')
                    coordinates.append({
                        'lat': float(lat.strip()),
                        'lon': float(lon.strip())
                    })
                except (ValueError, AttributeError) as e:
                    print(f"Ошибка обработки координат: {e}")
                    continue

        # Рассчитываем расстояние
        distance = route.calculate_distance()

        context = {
            'route': route,
            'coordinates': coordinates,
            'distance': distance,  # Добавляем расстояние в контекст
            'yandex_maps_api_key': settings.YANDEX_MAPS_API_KEY
        }

        return render(request, 'view_route.html', context)
    except Exception as e:
        print(f"Ошибка в view_route: {str(e)}")
        raise

@login_required
def add_route_view(request, research_id):
    print("DEBUG: Entering add_route_view")  # Добавьте эту строку
    research = get_object_or_404(Research, id=research_id, user=request.user)
    if request.method == 'POST':
        print("DEBUG: POST request received")  # Добавьте эту строку
        form = RouteForm(request.POST, request.FILES)
        if form.is_valid():
            print("DEBUG: Form is valid")  # Добавьте эту строку
            route = form.save(commit=False)
            route.research = research
            route.save()
            return redirect('research_detail', research_id=research.id)
        else:
            print("DEBUG: Form errors:", form.errors)  # Добавьте эту строку
    else:
        form = RouteForm()
    return render(request, 'add_route.html', {'form': form, 'research': research})

@login_required
def delete_route(request, research_id):
    research = get_object_or_404(Research, id=research_id, user=request.user)
    route = get_object_or_404(Route, research=research)

    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Маршрут успешно удален')
        return redirect('research_detail', research_id=research.id)

    return render(request, 'confirm_delete_route.html', {'research': research})


def forum_view(request):
    main_messages = ForumMessage.objects.filter(parent_message__isnull=True).order_by('-created_at')
    return render(request, 'forum.html', {
        'messages': main_messages,
        'request': request,
        'user': request.user  # Добавляем user в контекст
    })

@login_required
def create_forum_message(request):
    if request.method == 'POST':
        form = ForumMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            return redirect('forum')
    else:
        form = ForumMessageForm()
    return render(request, 'create_forum_message.html', {'form': form})

@login_required
def reply_forum_message(request, message_id):
    parent_message = get_object_or_404(ForumMessage, id=message_id)
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent_message = parent_message
            reply.title = f"Re: {parent_message.title}"
            reply.save()
            return redirect('forum')
    else:
        form = ForumReplyForm()
    return render(request, 'reply_forum_message.html', {
        'form': form,
        'parent_message': parent_message
    })

@login_required
def delete_forum_message(request, message_id):
    message = get_object_or_404(ForumMessage, id=message_id)

    if not message.can_delete(request.user):
        messages.error(request, "У вас нет прав для удаления этого сообщения")
        return redirect('forum')

    if request.method == 'POST':
        message.delete()
        messages.success(request, "Сообщение успешно удалено")
        return redirect('forum')

    return render(request, 'confirm_delete_message.html', {'message': message})

def installation_guide_view(request):
    return render(request, 'installation_guide.html')
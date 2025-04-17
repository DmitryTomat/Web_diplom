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
from .models import Research, ResearchFile, Defect
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Research, Defect
from .forms import XMLUploadForm
from .models import News
from .forms import NewsForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
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
def upload_xml_view(request):
    if request.method == 'POST':
        form = XMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Создаем новое исследование
            research = Research.objects.create(
                user=request.user,
                title=root.attrib['name'],
                description='',
                image=None,
                kml_file=None
            )

            # Обрабатываем дефекты
            defects_elem = root.find('.//Дефекты/pictures')
            if defects_elem is not None:
                for defect_elem in defects_elem:
                    picture_elem = defect_elem.find('picture')
                    description_elem = defect_elem.find('description')

                    defect = Defect.objects.create(
                        research=research,
                        defect_date=research.created_at,
                        defect_name=description_elem.find('defectText').text,
                        defect_description=description_elem.find('lengthDefect').text,
                        defect_coordinates=f"{picture_elem.attrib['latitude']}, {picture_elem.attrib['longitude']}",
                        defect_type=description_elem.find('defectType').text
                    )

            return redirect('research_detail', research_id=research.id)
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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, RegistrationForm
import json

@api_view(['POST'])
@permission_classes([])
def api_login(request):
    try:
        data = json.loads(request.body)
        form = LoginForm(data)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                return Response({
                    'status': 'success',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                })
            return Response({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'status': 'error',
            'errors': form.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])
def api_register(request):
    try:
        data = json.loads(request.body)
        form = RegistrationForm(data)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return Response({
                'status': 'success',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        return Response({
            'status': 'error',
            'errors': form.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
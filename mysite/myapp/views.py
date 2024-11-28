from django.contrib.auth import logout
from .forms import RegistrationForm
from .forms import UserForm
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User

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
                form.add_error(None, 'Invalid username or password')
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
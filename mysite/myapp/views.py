from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, RegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .forms import LoginForm, UserForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .forms import LoginForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:  # Проверка, является ли пользователь администратором
                    return redirect('admin_choice')
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def admin_choice_view(request):
    return render(request, 'admin_choice.html')

@user_passes_test(lambda u: u.is_staff)
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def user_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'user_detail.html', {'form': form, 'user': user})

@user_passes_test(lambda u: u.is_staff)
def user_delete_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'user_delete.html', {'user': user})

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
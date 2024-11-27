from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),
    path('software/', views.software_view, name='software'),
    path('about/', views.about_view, name='about'),
    path('news/', views.news_view, name='news'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('login_choice/', views.login_choice_view, name='login_choice'),
    path('settings/', views.settings_user, name='settings_user'),
]
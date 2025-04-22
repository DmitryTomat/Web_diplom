from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.api_login, name='api_login'),
    path('register/', views.api_register, name='api_register'),
    path('user/', views.get_user_data, name='api_user_data'),
]
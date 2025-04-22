from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('login/', obtain_auth_token, name='api_login'),
    path('register/', views.register_user, name='api_register'),
    path('user/', views.get_user_data, name='api_user_data'),
]
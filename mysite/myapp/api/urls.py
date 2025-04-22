from django.urls import path
from . import views

urlpatterns = [
    path('api/login/', views.api_login, name='api_login'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.api_login, name='api_login'),
]
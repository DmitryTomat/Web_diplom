from django.urls import path
from .views import login, get_researches

urlpatterns = [
    path('login/', login, name='api-login'),
    path('researches/', get_researches, name='api-researches'),
]
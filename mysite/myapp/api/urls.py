from django.urls import path
from . import api_views

urlpatterns = [
    path('login/', api_views.api_login, name='api_login'),
    path('register/', api_views.api_register, name='api_register'),
    path('profile/', api_views.api_profile, name='api_profile'),
    path('profile/update/', api_views.api_update_profile, name='api_update_profile'),
    path('users/', api_views.api_users, name='api_users'),
    path('researches/', api_views.api_researches, name='api_researches'),
    path('researches/<int:research_id>/', api_views.api_research_detail, name='api_research_detail'),
]
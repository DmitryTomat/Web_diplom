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
    path('users/', views.user_list_view, name='user_list'),
    path('users/delete/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('users/toggle_staff_status/<int:user_id>/', views.toggle_staff_status_view, name='toggle_staff_status'),
    path('research/', views.research_list_view, name='research_list'),
    path('research/create/', views.create_research_view, name='create_research'),
    path('users/<int:user_id>/research/', views.user_research_list_view, name='user_research_list'),
    path('research/sort/<str:sort_by>/<str:order>/', views.research_list_view, name='research_list_sorted'),
]
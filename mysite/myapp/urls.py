from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('admin_choice/', views.admin_choice_view, name='admin_choice'),
    path('user_list/', views.user_list_view, name='user_list'),
    path('user_detail/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('user_delete/<int:user_id>/', views.user_delete_view, name='user_delete'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('admin_choice/', views.admin_choice_view, name='admin_choice'),
    path('user_list/', views.user_list_view, name='user_list'),
    path('user_detail/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('user_delete/<int:user_id>/', views.user_delete_view, name='user_delete'),
    path('software/', views.software_view, name='software'),
    path('about/', views.about_view, name='about'),
    path('news/', views.news_view, name='news'),
    path('logout/', views.logout_view, name='logout'),
]
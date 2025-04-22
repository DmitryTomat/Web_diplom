from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),
    path('software/', views.software_view, name='software'),
    path('about/', views.about_view, name='about'),
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
    path('research/<int:research_id>/', views.research_detail_view, name='research_detail'),
    path('research/<int:research_id>/upload/', views.upload_file_view, name='upload_file'),
    path('research/<int:research_id>/edit/', views.edit_research_view, name='edit_research'),
    path('research/<int:research_id>/delete/', views.delete_research_view, name='delete_research'),
    path('research/<int:research_id>/add_defect/', views.add_defect_view, name='add_defect'),
    path('research/upload_xml/', views.upload_xml_view, name='upload_xml'),
    path('news/', views.news_view, name='news'),
    path('news/create/', views.create_news_view, name='create_news'),
    path('news/edit/<int:news_id>/', views.edit_news_view, name='edit_news'),
    path('news/delete/<int:news_id>/', views.delete_news_view, name='delete_news'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    path('api/', include('myapp.api.urls')),
    path('api/login/', views.api_login, name='api_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import api_views

urlpatterns = [
    path('login/', api_views.api_login, name='api_login'),
    path('register/', api_views.api_register, name='api_register'),
    path('profile/', api_views.api_profile, name='api_profile'),
    path('profile/update/', api_views.api_update_profile, name='api_update_profile'),
    path('research/', api_views.api_research, name='api_research'),
    path('defect/<int:defect_id>/', api_views.api_delete_defect, name='api_delete_defect'),
    path('research/upload/', api_views.api_upload_research, name='api_upload_research'),
    path('research/<int:research_id>/', api_views.api_research_detail, name='api_research_detail'),
]
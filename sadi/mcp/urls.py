# mcp/urls.py
from django.urls import path
from . import views

app_name = 'mcp'

urlpatterns = [
    path('', views.mcp_dashboard, name='dashboard'),
    path('api/chat/', views.mcp_api, name='api-chat'),
    path('api/report/', views.generate_report, name='generate-report'),
    path('conversations/', views.conversation_list, name='conversation-list'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation-detail'),
]

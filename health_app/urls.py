from django.urls import path
from . import views

app_name = 'health_app'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('chat/', views.chat_api, name='chat_api'),
    path('api/status/', views.api_status, name='api_status'),
]
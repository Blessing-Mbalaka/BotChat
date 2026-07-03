from django.urls import path
from . import views

app_name = 'health_app'

urlpatterns = [
    path('', views.course_view, name='course_home'),
    path('chat/', views.chat_api, name='chat_api'),
    path('api/extract/', views.extract_api, name='extract_api'),
    path('api/kpi/', views.kpi_api, name='kpi_api'),
    path('api/status/', views.api_status, name='api_status'),
    path('healthbot/', views.chatbot_view, name='chatbot'),
    # Course-related URLs
    path('course/', views.course_view, name='course'),
    path('course/chat/', views.course_chat_api, name='course_chat_api'),
    path('course/upload/', views.upload_pdf, name='upload_pdf'),
    path('course/stats/', views.course_stats, name='course_stats'),
    path('course/history/', views.search_course_history, name='search_course_history'),
    # Business School KPI URLs
    path('api/business-school-kpis/', views.business_school_kpis_api, name='business_school_kpis_api'),
    path('api/business-school-research/', views.business_school_research_api, name='business_school_research_api'),
    path('api/business-school-visualizations/', views.business_school_visualizations_api, name='business_school_visualizations_api'),
]

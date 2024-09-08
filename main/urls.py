from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.services_view, name='index'),
    path('service/<int:id>/', views.service_detail, name='service_detail'),
    
]
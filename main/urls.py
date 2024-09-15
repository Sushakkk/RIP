from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.GetServices, name='index'),
    path('service/<int:id>/', views.GetService, name='service'),
    path('basket/<int:count>/', views.GetBasket, name='basket'),  
]
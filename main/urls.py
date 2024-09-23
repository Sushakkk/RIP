from django.urls import path
from main import views
from .views import *


app_name = 'main'

urlpatterns = [
    path('', views.GetActivities, name='index'),
    path('activity/<int:id>/', views.GetActivity, name='activity'),
    path('activity/<int:activity_id>/add_activity/', add_activity),
    
    
    path('self-employed/', views.GetSelfEmployed, name='self-employed'),
    # path('self-employed/', views.GetSelfEmployed, name='self-employed'),
    
    
    
    
    
      
    path('self-employed/<int:self_employed_id>/',delete_self_employed),  
]
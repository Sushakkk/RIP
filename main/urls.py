from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.GetActivities, name='index'),
    path('activity/<int:id>/', views.GetActivity, name='activity'),
    # path('self-employed/<int:count>/', views.GetSelfEmployed, name='self-employed'),  
    path('self-employed/', views.GetSelfEmployed, name='self-employed'),  
]
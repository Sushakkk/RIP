from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для самозанятых
    
    path('api/self-employed/search/', search_self_employed),  # GET
    path('api/self-employed/<int:self_employed_id>/', get_self_employed_by_id),  # GET
    path('api/self-employed/<int:self_employed_id>/update/', update_self_employed),  # PUT
    path('api/self-employed/<int:self_employed_id>/update_by_creator/', update_by_creator),  # PUT
    path('api/self-employed/<int:self_employed_id>/update_by_moderator/', update_by_moderator),  # PUT
    path('api/self-employed/<int:self_employed_id>/delete/', delete_self_employed),  # DELETE
    
    path('api/user/<int:user_id>/draft/', get_draft_activities_list_for_user),  # GET
   
    


    # # Набор методов для деятельностей
     path('api/activities/', get_activities),  # GET
     path('api/activities/drafts/', get_activities_with_drafts),  # GET
    path('api/activities/<int:activity_id>/', get_activity_by_id),  # GET
    path('api/activities/create/', create_activity),  # POST
    path('api/activities/<int:activity_id>/update/', update_activity),  # PUT
    path('api/activities/<int:activity_id>/delete/', delete_activity),  # DELETE
    path('api/self-employed/<int:user_id>/add-activity/<int:activity_id>', add_activity),  # POST
    path('api/activities/<int:activity_id>/image/', update_activity_image),  # POST





    # # Набор методов для связей между самозанятыми и деятельностями
    path('api/self-employed/<int:user_id>/add/', create_self_employed_for_user),  # POST
    
    
    
     # # Набор методов М-М
    path('api/self-employed/<int:self_employed_id>/activity/<int:activity_id>/update_importance', update_importance),  # PUT
    
    path('api/self-employed-activities/<int:self_employed_id>/delete/<int:activity_id>', delete_self_employed_activity),  # DELETE

    # # Набор методов для пользователей
    path('api/user/register/', register),  # POST
    path('api/user/login/', login),  # POST
    path('api/user/logout/', logout),  # POST
    path('api/user/<int:user_id>/update/', update_user),  # PUT
]

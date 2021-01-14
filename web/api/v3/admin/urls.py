from django.urls import path
from . import views

urlpatterns = [
    path('users', views.get_users, name='api-v3-admin-get-users'),
    path('entities', views.get_entities, name='api-v3-admin-get-entities'),
    path('rights', views.get_rights, name='api-v3-admin-get-rights'),

    path('rights/add', views.add_rights, name='api-v3-admin-add-rights'),
    path('rights/delete', views.delete_rights, name='api-v3-admin-delete-rights'),
    path('entities/add', views.add_entity, name='api-v3-admin-add-entity'),
    path('entities/del', views.delete_entity, name='api-v3-admin-delete-entity'),
    path('users/add', views.add_user, name='api-v3-admin-add-user'),
    path('users/reset-password', views.reset_user_password, name='api-v3-admin-reset-user-password'),
    path('users/del', views.delete_user, name='api-v3-admin-delete-user'),
    
    path('lots', views.get_lots, name='api-v3-admin-get-lots'),
    path('lots/snapshot', views.get_snapshot, name='api-v3-admin-get-snapshot'),

]

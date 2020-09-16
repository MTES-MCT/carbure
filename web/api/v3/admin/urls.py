from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users, name='api-v3-admin-get-users'),
    path('entities/', views.get_entities, name='api-v3-admin-get-entities'),
    path('rights/', views.get_rights, name='api-v3-admin-get-rights'),
]

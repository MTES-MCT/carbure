from django.urls import path

from . import views

urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('password_reset', views.custom_password_reset, name='custom_password_reset'),
    path('password_reset_success', views.custom_password_reset_success, name='custom_password_reset_success'),            
]

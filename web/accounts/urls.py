from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('profile', views.profile, name='profile'),
    path('password_change', views.custom_password_change, name='custom_password_change'),
    path('password_change_success', views.custom_password_change_success, name='custom_password_change_success'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('account_activation_sent', views.account_activation_sent, name='account_activation_sent'),
    path('resend_activation_link', views.resend_activation_link, name='resend-activation-link'),
    path('activate', views.account_activation_sent, name='account_activation_sent'),


    path('hotp_verify', views.hotp_verify, name='hotp-verify'),
    path('profile', views.profile, name='profile'),
    path('password_change', views.custom_password_change, name='custom_password_change'),
    path('password_change_success', views.custom_password_change_success, name='custom_password_change_success'),
]

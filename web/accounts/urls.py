from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('account-activation-sent', views.account_activation_sent, name='account-activation-sent'),
    path('resend-activation-link', views.resend_activation_link, name='resend-activation-link'),
    path('activate/<str:uidb64>/<str:token>', views.activate, name='activate'),
    path('otp_verify', views.otp_verify, name='otp-verify'),
    path('resend_otp_code', views.resend_otp_code, name='resend-otp-code'),
    path('password-change', views.custom_password_change, name='custom-password-change'),
    path('password-change-success', views.custom_password_change_success, name='custom-password-change-success'),
]

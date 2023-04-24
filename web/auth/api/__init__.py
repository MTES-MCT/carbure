from django.urls import path
from .register import register
from .login import user_login
from .logout import user_logout
from .request_otp import request_otp
from .verify_otp import verify_otp
from .request_password_reset import request_password_reset
from .reset_password import reset_password
from .request_activation_link import request_activation_link
from .activate import activate

urlpatterns = [
    path("register", register, name="auth-register"),
    path("login", user_login, name="auth-login"),
    path("logout", user_logout, name="auth-logout"),
    path("request-otp", request_otp, name="auth-request-otp"),
    path("verify-otp", verify_otp, name="auth-verify-otp"),
    path("request-password-reset", request_password_reset, name="auth-request-password-reset"),
    path("reset-password", reset_password, name="auth-reset-password"),
    path("request-activation-link", request_activation_link, name="auth-request-activation-link"),
    path("activate", activate, name="auth-activate"),
]

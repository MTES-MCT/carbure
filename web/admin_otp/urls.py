"""
URLs for admin OTP authentication.
"""

from django.urls import path

from .views import OTPVerificationView, admin_otp_logout

app_name = "admin_otp"

urlpatterns = [
    path("verify/", OTPVerificationView.as_view(), name="otp_verify"),
    path("logout/", admin_otp_logout, name="logout"),
]

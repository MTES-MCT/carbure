from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext as _

from auth.views.mixins.request_otp import device_with_updated_validity
from core.helpers import send_mail
from core.utils import CarbureEnv


class AdminOTPMiddleware(MiddlewareMixin):
    """
    Middleware to intercept Django admin login and add OTP verification.

    Process:
    1. Intercepts POST requests to /admin/login/
    2. If credentials are valid, sends OTP and redirects to verification
    3. Enforces OTP verification for admin access
    """

    def process_request(self, request):
        if request.method == "GET" and request.path == "/admin/login/":
            # User is trying to start a new login, clear any pending OTP session
            if "otp_user_id" in request.session:
                del request.session["otp_user_id"]
            if "otp_next_url" in request.session:
                del request.session["otp_next_url"]

        if request.method == "POST" and request.path == "/admin/login/" and not request.session.get("otp_user_id"):
            return self._handle_admin_login_interception(request)

        if request.path.startswith("/admin/"):
            return self._enforce_otp_for_admin(request)

        return None

    def _handle_admin_login_interception(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return None  # Let Django handle missing credentials

        user = authenticate(request, username=username, password=password)
        if user is None:
            return None  # Let Django handle invalid credentials

        if not user.is_staff:
            return None  # Let Django handle non-staff users

        request.session["otp_user_id"] = user.id
        request.session["otp_next_url"] = request.POST.get("next", reverse("admin:index"))

        # Generate and send OTP
        device = device_with_updated_validity(user)
        self._send_email_change_token(request, device)

        return redirect("admin_otp:otp_verify")

    def _enforce_otp_for_admin(self, request):
        skip_urls = ["/admin/otp/", "/admin/login/", "/admin/logout/"]
        if any(request.path.startswith(url) for url in skip_urls):
            return None

        if not request.user.is_authenticated:
            return None

        if not request.user.is_staff:
            return redirect("admin:login")

        if not request.user.is_verified():
            request.session["otp_next_url"] = request.get_full_path()
            return redirect("admin:login")

        return None

    def _send_email_change_token(self, request, device):
        email_subject = _("Carbure - OTP connexion administrateur")
        device_validity = timezone.localtime(device.valid_until)
        expiry = "%s %s" % (device_validity.strftime("%H:%M"), device_validity.tzname())

        email_context = {
            "user": device.user,
            "otp_token": device.token,
            "token_expiry": expiry,
            "domain": CarbureEnv.get_base_url(),
        }

        html_message = loader.render_to_string("emails/admin_otp_token.html", email_context)
        text_message = loader.render_to_string("emails/admin_otp_token.txt", email_context)

        send_mail(
            request=request,
            subject=email_subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
            recipient_list=[device.user.email],
        )

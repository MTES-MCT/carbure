import pytz
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils import timezone
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.helpers import send_mail


class RequestOTPAction:
    @extend_schema(
        examples=[
            OpenApiExample(
                "Example response.",
                value={"valid_until": "07/03/2024, 14:09"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="request-otp")
    def request_otp(self, request):
        # send token by email and display form
        if not user_has_device(request.user):
            email_otp = EmailDevice()
            email_otp.user = request.user
            email_otp.name = "email"
            email_otp.confirmed = True
            email_otp.email = request.user.email
            email_otp.save()
        self.send_new_token(request)
        device = EmailDevice.objects.get(user=request.user)
        dt = device.valid_until.astimezone(pytz.timezone("Europe/Paris"))
        return Response(data={"valid_until": dt.strftime("%m/%d/%Y, %H:%M")})

    # static - not an endpoint
    def send_new_token(self, request):
        device = EmailDevice.objects.get(user=request.user)
        current_site = get_current_site(request)
        # if current token is expired, generate a new one
        now = timezone.now()
        if now > device.valid_until:
            device.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)
        email_subject = "Carbure - Code de Sécurité"
        dt = device.valid_until.astimezone(pytz.timezone("Europe/Paris"))
        expiry = "%s %s" % (dt.strftime("%H:%M"), dt.tzname())
        email_context = {
            "user": request.user,
            "domain": current_site.domain,
            "token": device.token,
            "token_expiry": expiry,
        }
        html_message = loader.render_to_string("emails/otp_token_email.html", email_context)
        text_message = loader.render_to_string("emails/otp_token_email.txt", email_context)
        send_mail(
            request=request,
            subject=email_subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
            recipient_list=[request.user.email],
        )

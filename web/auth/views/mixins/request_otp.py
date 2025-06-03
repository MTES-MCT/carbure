from django.conf import settings
from django.template import loader
from django.utils import timezone
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import CharField

from core.helpers import send_mail
from core.utils import CarbureEnv


class RequestOTPAction:
    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name="OtpResponse",
                fields={"valid_until": CharField()},
            ),
        },
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
        user = request.user
        # send token by email and display form
        if not user_has_device(user):
            self.create_device(user)
        self.send_new_token(request)
        device = EmailDevice.objects.get(user=request.user)
        device_validity = self.device_validity_in_local_timezone(device)
        return Response({"valid_until": device_validity.strftime("%m/%d/%Y, %H:%M")})

    def create_device(self, user):
        email_otp = EmailDevice()
        email_otp.user = user
        email_otp.name = "email"
        email_otp.confirmed = True
        email_otp.email = user.email
        email_otp.save()

    def device_validity_in_local_timezone(self, device):
        return timezone.localtime(device.valid_until)

    # static - not an endpoint
    def send_new_token(self, request):
        device = EmailDevice.objects.get(user=request.user)
        # if current token is expired, generate a new one
        now = timezone.now()
        if now > device.valid_until:
            device.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)
        email_subject = "Carbure - Code de Sécurité"
        device_validity = self.device_validity_in_local_timezone(device)
        expiry = "%s %s" % (device_validity.strftime("%H:%M"), device_validity.tzname())
        email_context = {
            "user": request.user,
            "domain": CarbureEnv.get_base_url(),
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

from django.utils import timezone
from django_otp import login as login_with_device
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from auth.serializers import VerifyOTPSerializer
from core.carburetypes import CarbureError


class VerifyOTPAction:
    @extend_schema(
        request=VerifyOTPSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        # for old users that did not register when 2fa was introduced
        if not user_has_device(request.user):
            email_otp = EmailDevice()
            email_otp.user = request.user
            email_otp.name = "email"
            email_otp.confirmed = True
            email_otp.email = request.user.email
            email_otp.save()

        serializer = VerifyOTPSerializer(data=request.data, user=request.user)
        serializer.is_valid(raise_exception=True)
        device = EmailDevice.objects.get(user=request.user)
        otp_token = serializer.validated_data["otp_token"]

        if device.verify_token(otp_token):
            login_with_device(request, device)
            return Response({"status": "success"})
        else:
            is_allowed, _ = device.verify_is_allowed()
            now = timezone.now()
            if now > device.valid_until:
                raise ValidationError({"message": CarbureError.OTP_EXPIRED_CODE})
            elif device.token != otp_token:
                raise ValidationError({"message": CarbureError.OTP_INVALID_CODE})
            elif not is_allowed:
                raise ValidationError({"message": CarbureError.OTP_RATE_LIMITED})
            else:
                raise ValidationError({"message": CarbureError.OTP_UNKNOWN_ERROR})

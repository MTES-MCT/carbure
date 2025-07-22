from django.utils import timezone
from django.utils.translation import gettext as _
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


class VerifyOTPAction:
    throttle_scope = "10/day"

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

        is_allowed, reason = device.verify_is_allowed()
        if not is_allowed:
            locked_until_utc = reason.get("locked_until")
            locked_until_local = timezone.localtime(locked_until_utc)
            formatted_time = locked_until_local.strftime("%H:%M:%S")
            failure_count = reason.get("failure_count", 0)

            raise ValidationError(
                {
                    "message": _("Trop de tentatives incorrectes (%d échecs). Prochaine tentative possible à partir de %s.")
                    % (failure_count, formatted_time)
                }
            )

        now = timezone.now()
        if now > device.valid_until:
            raise ValidationError({"message": _("Le code de sécurité a expiré. Veuillez demander un nouveau code.")})

        if device.verify_token(otp_token):
            login_with_device(request, device)
            return Response({"status": "success"})
        else:
            raise ValidationError({"message": _("Le code de sécurité est incorrect.")})

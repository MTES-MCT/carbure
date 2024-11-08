from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import ResetPasswordSerializer
from core.carburetypes import CarbureError


class ResetPasswordAction:
    @extend_schema(
        request=ResetPasswordSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = serializer.validated_data.get("uidb64", "")
        token = serializer.validated_data.get("token", "")

        password = serializer.validated_data.get("password1", "")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        prtg = PasswordResetTokenGenerator()
        if prtg.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({"status": "success"})
        else:
            return Response(
                {
                    "message": CarbureError.PASSWORD_RESET_INVALID_FORM,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.carburetypes import CarbureError
from core.helpers import send_mail


class RequestPasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)


class RequestPasswordResetAction:
    @extend_schema(
        request=RequestPasswordResetSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="request-password-reset")
    def request_password_reset(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username", "")

        user = get_user_model().objects.filter(email=username).first()
        if not user:
            return Response(
                {"message": CarbureError.PASSWORD_RESET_USER_NOT_FOUND},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prtg = PasswordResetTokenGenerator()
        current_site = get_current_site(request)
        # send email
        email_subject = "Carbure - Réinitialisation du mot de passe"
        email_context = {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": prtg.make_token(user),
        }
        html_message = loader.render_to_string("emails/password_reset_email.html", email_context)
        text_message = loader.render_to_string("emails/password_reset_email.txt", email_context)
        send_mail(
            request=request,
            subject=email_subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
            recipient_list=[user.email],
        )

        return Response({"status": "success"})

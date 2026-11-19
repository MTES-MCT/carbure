import logging

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.views.mixins.mail_helper import send_account_activation_email

logger = logging.getLogger(__name__)


def user_from_email(data):
    serializer = UserResendActivationLinkSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return get_user_model().objects.get(email__iexact=serializer.validated_data["email"])


class UserResendActivationLinkAction:
    @extend_schema(
        request=UserResendActivationLinkSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="RequestActivationLinkSuccess",
                    fields={"status": serializers.CharField(default="success")},
                ),
                description="The request was accepted. A mail is sent only when a pending account matches the address.",
            ),
        },
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="request-activation-link", throttle_scope="auth-anon")
    def request_activation_link(self, request):
        try:
            user = user_from_email(request.data)
            # Only a pending account gets a new mail. An active one, an unknown address
            # and a send failure all look the same, so the form cannot be used to probe accounts.
            if not user.is_active:
                send_account_activation_email(user, request)
        except (get_user_model().DoesNotExist, ValidationError):
            pass
        except Exception:
            logger.exception("Could not resend the activation link")
        return Response({"status": "success"})

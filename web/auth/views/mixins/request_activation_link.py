from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.views.mixins.mail_helper import send_account_activation_email


def user_from_email(data):
    serializer = UserResendActivationLinkSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return get_user_model().objects.get(email__iexact=serializer.validated_data["email"])


class UserResendActivationLinkAction:
    @extend_schema(
        request=UserResendActivationLinkSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
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
        except Exception:
            pass  # Do not expose user existence to avoid enumeration attacks
        return Response({"status": "success"})

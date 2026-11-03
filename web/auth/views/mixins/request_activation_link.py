from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.views.mixins.mail_helper import send_account_activation_email


def email_from(data):
    serializer = UserResendActivationLinkSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data.get("email", "")


def retrieve_user(data):
    usermodel = get_user_model()
    email = email_from(data)
    return usermodel.objects.get(email__iexact=email)


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
            user = retrieve_user(request.data)
            if not user.is_active:
                send_account_activation_email(user, request)
        except Exception:
            pass  # Do not expose user existence to avoid enumeration attacks
        return Response({"status": "success"})

from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.tokens import account_activation_token
from auth.views.mixins.mail_helper import send_account_activation_email


def retrieve_user(data):
    serializer = UserResendActivationLinkSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    usermodel = get_user_model()
    email = serializer.validated_data.get("email")
    if email:
        return usermodel.objects.get(email__iexact=email)

    uidb64 = serializer.validated_data.get("uidb64")
    token = serializer.validated_data.get("token")
    if not uidb64:
        raise usermodel.DoesNotExist
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = usermodel.objects.get(pk=uid)
    if not account_activation_token.was_issued_for(user, token):
        raise usermodel.DoesNotExist
    return user


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

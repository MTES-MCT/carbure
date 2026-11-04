from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.tokens import account_activation_token
from auth.views.mixins.mail_helper import send_account_activation_email
from core.carburetypes import CarbureError


def user_from_email(data):
    serializer = UserResendActivationLinkSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get("email")
    if not email:
        raise get_user_model().DoesNotExist
    return get_user_model().objects.get(email__iexact=email)


def user_from_uid(uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return get_user_model().objects.get(pk=uid)
    except Exception:
        return None


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
        # The button on an activation link sends the account id; the email form does not.
        if request.data.get("uidb64"):
            return self.resend_from_link(request)
        return self.resend_from_email(request)

    def resend_from_email(self, request):
        try:
            user = user_from_email(request.data)
            # Only a pending account gets a new mail. An active one, an unknown address
            # and a send failure all look the same, so the form cannot be used to probe accounts.
            if not user.is_active:
                send_account_activation_email(user, request)
        except Exception:
            pass  # Do not expose user existence to avoid enumeration attacks
        return Response({"status": "success"})

    def resend_from_link(self, request):
        serializer = UserResendActivationLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_from_uid(serializer.validated_data.get("uidb64", ""))
        token = serializer.validated_data.get("token", "")
        # Unknown id uses the same error as a bad token: the response must not confirm that a pk exists.
        if user is None:
            return Response({"message": CarbureError.ACTIVATION_LINK_ERROR}, status=status.HTTP_400_BAD_REQUEST)

        # Recompute the signature as if the account were still inactive. It matches only the link
        # issued before activation, so "already active" is not returned from the account id alone.
        issued_before_activation = account_activation_token.was_issued_for(user, token, is_active=False)
        if user.is_active and issued_before_activation:
            return Response({"message": CarbureError.ACCOUNT_ALREADY_ACTIVE}, status=status.HTTP_400_BAD_REQUEST)

        # Active with any other token, or inactive but the token does not match (rotated secret,
        # another account): no mail. Expiry is ignored here, a merely expired link still matches.
        if user.is_active or not account_activation_token.was_issued_for(user, token):
            return Response({"message": CarbureError.ACTIVATION_LINK_ERROR}, status=status.HTTP_400_BAD_REQUEST)

        # Nothing was written if the account was activated since it was loaded.
        if not send_account_activation_email(user, request):
            return Response({"message": CarbureError.ACTIVATION_LINK_ERROR}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "success"})

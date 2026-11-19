from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import ActivateAccountSerializer
from auth.tokens import account_activation_token
from core.carburetypes import CarbureError


class ActivateAccountAction:
    @extend_schema(
        request=ActivateAccountSerializer,
        responses={
            400: OpenApiResponse(
                response={"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                description="Bad request - missing fields.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                summary="A successful activation",
                description="The account was successfully activated.",
                value={},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                summary="Activation failed",
                value={"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], throttle_scope="auth-anon")
    def activate(self, request):
        serializer = ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = serializer.validated_data.get("uidb64", "")
        token = serializer.validated_data.get("token", "")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except Exception:
            user = None

        # An invited account has no password yet. It is finished by activate-profile,
        # which collects the name. Activating it here would skip that step.
        if (
            user is None
            or user.is_active
            or not user.has_usable_password()
            or not account_activation_token.check_token(user, token)
        ):
            return Response(
                {"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({})

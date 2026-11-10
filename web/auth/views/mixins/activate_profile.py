from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import ActivateAccountSerializer, ActivateProfileSerializer
from auth.tokens import account_activation_token
from core.carburetypes import CarbureError


def invited_user_from_link(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except Exception:
        return None
    token_matches = account_activation_token.check_token(user, token)
    if user.is_active or user.has_usable_password() or not token_matches:
        return None
    return user


class ActivateProfileAction:
    @extend_schema(
        request=ActivateAccountSerializer,
        responses={
            200: OpenApiResponse(description="The invitation link is still valid."),
            400: OpenApiResponse(
                response={"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                description="The link is expired, already used, or does not belong to an invited account.",
            ),
        },
    )
    @action(detail=False, methods=["post"], url_path="activate-profile/check", throttle_scope="auth-anon")
    def check_activate_profile(self, request):
        # The join page asks before showing the form. An expired link must not display it.
        serializer = ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = invited_user_from_link(serializer.validated_data["uidb64"], serializer.validated_data["token"])
        if user is None:
            return Response(
                {"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({})

    @extend_schema(
        request=ActivateProfileSerializer,
        responses={
            200: OpenApiResponse(description="The account was activated and the password was set."),
            400: OpenApiResponse(
                response={"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                description="The link is no longer valid, or the account already has a password.",
            ),
        },
    )
    @action(detail=False, methods=["post"], url_path="activate-profile", throttle_scope="auth-anon")
    def activate_profile(self, request):
        link = ActivateAccountSerializer(data=request.data)
        if not link.is_valid():
            return Response(
                {"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = link.validated_data["token"]
        user = invited_user_from_link(link.validated_data["uidb64"], token)
        if user is None:
            return Response(
                {"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ActivateProfileSerializer(user, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        name = serializer.validated_data["name"]
        password = serializer.validated_data["password1"]

        with transaction.atomic():
            locked = get_user_model().objects.select_for_update().get(pk=user.pk)
            link_still_valid = account_activation_token.check_token(locked, token)
            if locked.is_active or locked.has_usable_password() or not link_still_valid:
                return Response(
                    {"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            locked.name = name
            locked.set_password(password)
            locked.is_active = True
            locked.save(update_fields=["name", "password", "is_active"])

        return Response({})

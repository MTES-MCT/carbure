from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import CharField

from auth.serializers import ActivateAccountSerializer
from auth.tokens import account_activation_token
from core.carburetypes import CarbureError


class ActivateAccountAction:
    @extend_schema(
        request=ActivateAccountSerializer,
        responses={
            200: inline_serializer(
                name="ActivateResponse",
                fields={
                    "message": CharField(),
                    "token": CharField(required=False),
                },
            ),
            # OpenApiResponse(
            #     response={"status": "success"},
            #     description="Request successful.",
            # )
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
                value={"status": "success"},
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
    @action(detail=False, methods=["post"])
    def activate(self, request):
        serializer = ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = serializer.validated_data.get("uidb64", "")
        token = serializer.validated_data.get("token", "")
        invite = serializer.validated_data.get("invite", 0)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
        except Exception:
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)

            data = {}

            if invite:
                # Generate token to let new user change his password
                prtg = PasswordResetTokenGenerator()
                passtoken = prtg.make_token(user)
                data = {"token": passtoken}

            return Response(data=data)
        else:
            return Response(
                {"message": CarbureError.ACTIVATION_COULD_NOT_ACTIVATE_USER},
                status=status.HTTP_400_BAD_REQUEST,
            )

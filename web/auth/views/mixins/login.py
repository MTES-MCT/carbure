from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as django_login
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserLoginSerializer
from core.carburetypes import CarbureError


class UserLoginAction:
    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": f"{CarbureError.INVALID_LOGIN_CREDENTIALS} | {CarbureError.ACCOUNT_NOT_ACTIVATED}"},
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
                summary="login failed",
                value={"message": f"{CarbureError.INVALID_LOGIN_CREDENTIALS} | {CarbureError.ACCOUNT_NOT_ACTIVATED}"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username", "")
        password = serializer.validated_data.get("password", "")
        User = get_user_model()

        user = authenticate(username=username, password=password)
        try:
            if user.is_authenticated:
                django_login(request, user)
                request.session.set_expiry(3 * 30 * 24 * 60 * 60)  # 3 months

                return Response({"status": "success", "message": "User logged in"})
            else:
                return Response(
                    {"message": CarbureError.INVALID_LOGIN_CREDENTIALS},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception:
            user = User.objects.filter(email=username).first()
            if user and user.check_password(password):
                message = CarbureError.ACCOUNT_NOT_ACTIVATED
            else:
                message = CarbureError.INVALID_LOGIN_CREDENTIALS
            return Response(
                {"message": message},
                status=status.HTTP_400_BAD_REQUEST,
            )

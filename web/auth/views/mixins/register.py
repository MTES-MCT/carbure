from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserCreationSerializer
from auth.views.mixins.mail_helper import send_account_activation_email

User = get_user_model()


class UserCreationAction:
    throttle_scope = "10/day"

    @extend_schema(
        request=UserCreationSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                status_codes=[200],
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        user_already_exists = User.objects.filter(email=email).exists()

        if not user_already_exists:
            user = serializer.save()
            send_account_activation_email(user, request)

        # Always return the same response to avoid enumeration
        return Response({"status": "success"})

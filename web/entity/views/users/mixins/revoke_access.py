from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity, UserRights, UserRightsRequests

User = get_user_model()


class RevokeUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Normalize and validate email existence."""
        normalized_email = User.objects.normalize_email(value)
        if not User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return normalized_email


class RevokeUserActionMixin:
    @extend_schema(
        request=RevokeUserSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="revoke-access")
    def revoke_access(self, request):
        entity_id = self.request.query_params.get("entity_id")

        entity = Entity.objects.get(id=entity_id)
        serializer = RevokeUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")

        try:
            user = User.objects.get(email=email)
        except Exception:
            return Response(
                {"status": "error", "message": "Could not find user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            UserRights.objects.filter(user=user, entity=entity).delete()
        except Exception:
            pass

        try:
            rr = UserRightsRequests.objects.get(user=user, entity=entity)
            rr.status = "REVOKED"
            rr.save()
        except Exception:
            pass

        return Response({"status": "success"})

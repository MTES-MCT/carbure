from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import UserRights, UserRightsRequests

User = get_user_model()


class ChangeRoleSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)

    def validate_email(self, value):
        """Normalize and validate email existence."""
        normalized_email = User.objects.normalize_email(value)
        if not User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return normalized_email

    def validate_role(self, value):
        """Ensure the role is valid."""
        if value not in dict(UserRights.ROLES):
            raise serializers.ValidationError("INVALID_ROLE")
        return value


class ChangeUserRoleError:
    MISSING_USER = "MISSING_USER"
    NO_PRIOR_RIGHTS = "NO_PRIOR_RIGHTS"
    UPDATE_FAILED = "UPDATE_FAILED"


class ChangeRoleActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=ChangeRoleSerializer,
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
    @action(detail=False, methods=["post"], url_path="change-role")
    def change_role(self, request):
        entity_id = self.request.query_params.get("entity_id")

        serializer = ChangeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email", "")
        role = serializer.validated_data.get("role", "")

        try:
            user = User.objects.get(email=email)
        except Exception:
            return Response(
                {"message": ChangeUserRoleError.MISSING_USER},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rights = UserRights.objects.filter(user=user, entity_id=entity_id).first()
        rights_request = UserRightsRequests.objects.filter(user=user, entity_id=entity_id).first()

        if not rights and not rights_request:
            return Response(
                {"message": ChangeUserRoleError.NO_PRIOR_RIGHTS},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if rights:
            rights.role = role
            rights.save()
        if rights_request:
            rights_request.role = role
            rights_request.save()

        return Response({"status": "success"})

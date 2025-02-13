from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import UserRights, UserRightsRequests


class UpdateUserRoleSerializer(serializers.Serializer):
    request_id = serializers.PrimaryKeyRelatedField(queryset=UserRightsRequests.objects.all())
    role = serializers.CharField(required=True)


class UpdatUserRoleActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        request=UpdateUserRoleSerializer,
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
    @action(detail=False, methods=["post"], url_path="update-user-role")
    def update_user_role(self, request):
        serializer = UpdateUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        right_request = serializer.validated_data.get("request_id")
        role = serializer.validated_data.get("role")

        with transaction.atomic():
            right_request.role = role
            right_request.save()

            rights = UserRights.objects.filter(entity_id=right_request.entity_id, user_id=right_request.user_id)
            rights.update(role=role)
        return Response({"status": "success"})

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity


class ToggleRFCSerializer(serializers.Serializer):
    has_mac = serializers.BooleanField(default=False)


class ToggleRFCActionMixin:
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
        request=ToggleRFCSerializer,
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
    @action(detail=False, methods=["post"], url_path="release-for-consumption")
    def release_for_consumption(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = ToggleRFCSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        has_mac = serializer.validated_data.get("has_mac", False)

        entity.has_mac = has_mac
        entity.save()

        return Response({"status": "success"})

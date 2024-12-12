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


class DirectDeliveriesSerializer(serializers.Serializer):
    has_direct_deliveries = serializers.BooleanField(default=False)


class DirectDeliveriesActionMixin:
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
        request=DirectDeliveriesSerializer,
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
    @action(detail=False, methods=["post"], url_path="direct-deliveries")
    def direct_deliveries(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = DirectDeliveriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        has_direct_deliveries = serializer.validated_data.get("has_direct_deliveries", False)

        entity.has_direct_deliveries = has_direct_deliveries
        entity.save()

        return Response({"status": "success"})

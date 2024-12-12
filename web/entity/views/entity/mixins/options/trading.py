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


class ToggleTradingSerializer(serializers.Serializer):
    has_trading = serializers.BooleanField(default=False)


class ToggleTradingActionMixin:
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
        request=ToggleTradingSerializer,
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
    @action(detail=False, methods=["post"])
    def trading(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = ToggleTradingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        has_trading = serializer.validated_data.get("has_trading", False)

        entity.has_trading = has_trading
        entity.save()

        return Response({"status": "success"})

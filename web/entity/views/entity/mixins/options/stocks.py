from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import CarbureStock, Entity


class ToggleStocksSerializer(serializers.Serializer):
    has_stocks = serializers.BooleanField(default=False)


class ToggleStocksActionMixin:
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
        request=ToggleStocksSerializer,
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
    def stocks(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = ToggleStocksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        has_stocks = serializer.validated_data.get("has_stocks", False)

        if not has_stocks:
            stocks = CarbureStock.objects.filter(carbure_client=entity)
            if stocks.count() > 0:
                return Response(
                    {"message": "Cannot disable stocks if you have stocks"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        entity.has_stocks = has_stocks
        entity.save()

        return Response({"status": "success"})

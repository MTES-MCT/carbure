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


class UnitSerializer(serializers.Serializer):
    UnitChoices = (("l", "litres"), ("kg", "kg"), ("MJ", "MJ"))
    unit = serializers.ChoiceField(choices=UnitChoices, default="l")


class UnitActionMixin:
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
        request=UnitSerializer,
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
    @action(detail=False, methods=["post"], url_path="unit")
    def preferred_unit(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = UnitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unit = serializer.validated_data.get("unit", "l")

        entity.preferred_unit = unit
        entity.save()

        return Response({"status": "success"})

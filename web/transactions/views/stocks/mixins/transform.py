from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.helpers import handle_eth_to_etbe_transformation
from core.models import CarbureStock, CarbureStockTransformation, Entity


class TransformSerCreateSerializer(serializers.Serializer):
    stock_id = serializers.CharField(max_length=255)
    transformation_type = serializers.ChoiceField(choices=CarbureStockTransformation.TRANSFORMATION_TYPES)
    volume_ethanol = serializers.FloatField(required=False)
    volume_etbe = serializers.FloatField(required=False)
    volume_denaturant = serializers.FloatField(required=False)
    volume_etbe_eligible = serializers.FloatField(required=False)


class TransformSerializer(serializers.Serializer):
    payload = TransformSerCreateSerializer(many=True)

    def validate_payload(self, value):
        if not value:
            raise serializers.ValidationError("The payload field must not be empty.")

        if not isinstance(value, list):
            raise serializers.ValidationError("Parsed JSON is not a list")
        return value


class TransformMixin:
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
        request=TransformSerializer,
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False)
    def transform(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")

        entity = get_object_or_404(Entity, id=entity_id)

        serializer = TransformSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data["payload"]

        for entry in payload:
            # check minimum fields
            required_fields = ["stock_id", "transformation_type"]
            for field in required_fields:
                if field not in entry:
                    raise ValidationError({"message": f"Missing field {field} in json object"})

            try:
                stock = CarbureStock.objects.get(pk=entry["stock_id"])
            except Exception:
                raise ValidationError({"message": "Could not find stock"})

            if stock.carbure_client != entity:
                raise PermissionDenied({"message": "Stock does not belong to you"})

            ttype = entry["transformation_type"]
            if ttype == CarbureStockTransformation.ETH_ETBE:
                error = handle_eth_to_etbe_transformation(request.user, stock, entry)
                if error:
                    return error

        return Response({"status": "success"})

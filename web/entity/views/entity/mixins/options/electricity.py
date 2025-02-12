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

from core.models import Entity


class ToggleElecError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    NOT_OPERATOR = "NOT_OPERATOR"


class ToggleElecSerializer(serializers.Serializer):
    has_elec = serializers.BooleanField(default=False)


class ToggleElecActionMixin:
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
        request=ToggleElecSerializer,
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
    def elec(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = ToggleElecSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        has_elec = serializer.validated_data.get("has_elec", False)

        if entity.entity_type != Entity.OPERATOR:
            return Response({"message": ToggleElecError.NOT_OPERATOR}, status=status.HTTP_400_BAD_REQUEST)

        entity.has_elec = has_elec
        entity.save()

        return Response({"status": "success"})

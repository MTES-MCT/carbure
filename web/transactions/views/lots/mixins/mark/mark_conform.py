import traceback

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import CarbureLot


class MarkConformSerializer(serializers.Serializer):
    selection = serializers.ListField(child=serializers.IntegerField())


class MarkConformMixin:
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
        request=MarkConformSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="mark-conform")
    def mark_conform(self, request, *args, **kwargs):
        serializer = MarkConformSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data["selection"]
        try:
            lots = CarbureLot.objects.filter(id__in=selection)
            lots.update(audit_status=CarbureLot.CONFORM)
            return Response({"status": "success"})
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": "Could not mark lots as conform"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

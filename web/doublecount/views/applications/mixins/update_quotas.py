import json

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from doublecount.models import DoubleCountingProduction

from .response_serializer import ResponseSerializer


class UpdatedQuotasSerializer(serializers.Serializer):
    approved_quotas = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2)
    )


class UpdateQuotaActionMixin:
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
        request=UpdatedQuotasSerializer,
        responses={200: ResponseSerializer},
        examples=[
            OpenApiExample(
                "Example of response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="update-approved-quotas")
    def update_approved_quotas(self, request):
        approved_quotas = request.data.get("approved_quotas")
        if isinstance(approved_quotas, str):
            try:
                approved_quotas = json.loads(approved_quotas)
            except json.JSONDecodeError:
                return Response(
                    {"error": "Format JSON invalide pour approved_quotas."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        data = {"approved_quotas": approved_quotas}
        serializer = UpdatedQuotasSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        approved_quotas = serializer.validated_data["approved_quotas"]

        for dca_production_id, approved_quota in approved_quotas:
            try:
                to_update = DoubleCountingProduction.objects.get(id=dca_production_id)
                to_update.approved_quota = approved_quota
                to_update.save()
            except Exception:
                return Response(
                    {"status": "error", "message": "Could not find Production Line"},
                    status=400,
                )
        return Response({"status": "success"})

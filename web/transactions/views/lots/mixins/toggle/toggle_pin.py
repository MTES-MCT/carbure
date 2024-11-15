import traceback

from django.db.models import Case, Value, When
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import CarbureLot, Entity


class TogglePinSerializer(serializers.Serializer):
    selection = serializers.ListField(child=serializers.IntegerField())
    notify_admin = serializers.BooleanField(default=False)
    notify_auditor = serializers.BooleanField(default=False)


class TogglePinMixin:
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
        request=TogglePinSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="toggle-pin")
    def toggle_pin(self, request, *args, **kwargs):
        entity_id = self.request.query_params.get("entity_id")
        entity = get_object_or_404(Entity, id=entity_id)
        serializer = TogglePinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data["selection"]
        notify_admin = serializer.validated_data.get("notify_admin")
        notify_auditor = serializer.validated_data.get("notify_auditor")

        try:
            lots = CarbureLot.objects.filter(id__in=selection)
            if entity.entity_type == Entity.AUDITOR:
                lots.update(
                    highlighted_by_auditor=Case(
                        When(highlighted_by_auditor=True, then=Value(False)),
                        When(highlighted_by_auditor=False, then=Value(True)),
                    )
                )
                if notify_admin:
                    lots.update(highlighted_by_admin=True)
            elif entity.entity_type == Entity.ADMIN:
                lots.update(
                    highlighted_by_admin=Case(
                        When(highlighted_by_admin=True, then=Value(False)),
                        When(highlighted_by_admin=False, then=Value(True)),
                    )
                )
                if notify_auditor:
                    lots.update(highlighted_by_auditor=True)

            return Response({"status": "success"})
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": "Could not pin lots"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

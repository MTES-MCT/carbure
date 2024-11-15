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

from core.models import Entity, GenericError


class ToggleWarningSerializer(serializers.Serializer):
    errors = serializers.ListField(child=serializers.CharField(max_length=255))
    checked = serializers.BooleanField(required=False, default=False)

    def validate_errors(self, value):
        if not value:
            raise serializers.ValidationError("The error list must not be empty.")
        return value


class ToggleWarningMixin:
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
        request=ToggleWarningSerializer,
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=True, url_path="toggle-warning")
    def toggle_warning(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        serializer = ToggleWarningSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        errors = serializer.validated_data["errors"]
        checked = serializer.validated_data["checked"]
        lot = self.get_object()
        entity = Entity.objects.get(id=entity_id)
        try:
            for error in errors:
                try:
                    lot_error = GenericError.objects.get(lot_id=lot.id, error=error)
                except Exception:
                    traceback.print_exc()
                    return Response(
                        {"message": "Could not locate wanted error"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                if entity.entity_type == Entity.AUDITOR:
                    lot_error.acked_by_auditor = checked
                elif entity.entity_type == Entity.ADMIN:
                    lot_error.acked_by_admin = checked
                else:
                    # is creator
                    if lot.added_by_id == int(entity_id):
                        lot_error.acked_by_creator = checked
                    # is recipient
                    if lot.carbure_client_id == int(entity_id):
                        lot_error.acked_by_recipient = checked
                lot_error.save()
            return Response({"status": "success"})
        except Exception:
            return Response(
                {"message": "Error creating template file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

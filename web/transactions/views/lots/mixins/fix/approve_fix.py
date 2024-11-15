from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import CarbureLot, CarbureLotEvent


class ApproveFixError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    UNAUTHORIZED_ENTITY = "UNAUTHORIZED_ENTITY"


class ApproveFixSerializer(serializers.Serializer):
    # config fields
    lot_ids = serializers.PrimaryKeyRelatedField(queryset=CarbureLot.objects.all(), many=True)


class ApprouveFixMixin:
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
        request=ApproveFixSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["post"], detail=False, url_path="approuve-fix")
    def approve_fix(self, request, *args, **kwargs):
        entity_id = int(self.request.query_params.get("entity_id"))

        serializer = ApproveFixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lot_instances = serializer.validated_data["lot_ids"]

        lot_ids = [lot.id for lot in lot_instances]

        lots = CarbureLot.objects.filter(id__in=lot_ids)

        approve_fix_events = []

        for lot in lots:
            if lot.carbure_client_id != entity_id:
                return Response({"error": ApproveFixError.UNAUTHORIZED_ENTITY}, status=status.HTTP_400_BAD_REQUEST)

            event = CarbureLotEvent(event_type=CarbureLotEvent.FIX_ACCEPTED, lot=lot, user=request.user)
            approve_fix_events.append(event)

        with transaction.atomic():
            lots.update(correction_status=CarbureLot.NO_PROBLEMO)
            CarbureLotEvent.objects.bulk_create(approve_fix_events)

        return Response({"status": "success"})

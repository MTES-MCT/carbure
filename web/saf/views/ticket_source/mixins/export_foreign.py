from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.models import Entity
from saf.models import SafTicketSource, create_export_ticket_from_source
from saf.serializers import SafTicketSourceExportSerializer

from .utils import SafTicketAssignError


class ExportForeignActionMixin:
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
        examples=[
            OpenApiExample(
                "Example of export response.",
                value={},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="export-foreign",
        serializer_class=SafTicketSourceExportSerializer,
    )
    def export_foreign(self, request, id=None):
        entity_id = int(request.query_params.get("entity_id"))

        if (
            not Entity.objects.filter(id=entity_id)
            .filter(Q(entity_type=Entity.OPERATOR, has_saf=True) | Q(entity_type=Entity.SAF_TRADER))
            .exists()
        ):
            raise PermissionDenied()

        ticket_source = get_object_or_404(SafTicketSource, id=id, added_by_id=entity_id)

        serializer = SafTicketSourceExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        volume = serializer.validated_data["volume"]
        assignment_period = serializer.validated_data["assignment_period"]
        export_country = serializer.validated_data["export_country"]
        unknown_airline_client = serializer.validated_data["unknown_airline_client"]

        if volume > (ticket_source.total_volume - ticket_source.assigned_volume):
            raise ValidationError({"message": SafTicketAssignError.VOLUME_TOO_BIG})

        if assignment_period < ticket_source.delivery_period:
            raise ValidationError({"message": SafTicketAssignError.ASSIGNMENT_BEFORE_DELIVERY})

        with transaction.atomic():
            ticket = create_export_ticket_from_source(
                ticket_source,
                volume=volume,
                assignment_period=assignment_period,
                export_country=export_country,
                unknown_airline_client=unknown_airline_client,
            )

            ticket_source.assigned_volume += ticket.volume
            ticket_source.save()

        return Response({}, status=status.HTTP_200_OK)

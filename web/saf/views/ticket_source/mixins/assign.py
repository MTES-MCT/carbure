import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureNotification
from saf.models import SafTicketSource, create_ticket_from_source
from saf.serializers import SafTicketSourceAssignmentSerializer

from .utils import SafTicketAssignError


class AssignActionMixin:
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
                "Example of assign response.",
                value={},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(
        methods=["post"],
        detail=True,
        serializer_class=SafTicketSourceAssignmentSerializer,
    )
    def assign(self, request, id=None):
        entity_id = int(request.query_params.get("entity_id"))
        ticket_source = get_object_or_404(SafTicketSource, id=id, added_by_id=entity_id)

        serializer = SafTicketSourceAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = serializer.validated_data["client_id"]
        volume = serializer.validated_data["volume"]
        agreement_reference = serializer.validated_data["agreement_reference"]
        agreement_date = serializer.validated_data["agreement_date"]
        free_field = serializer.validated_data.get("free_field")
        assignment_period = serializer.validated_data["assignment_period"]

        if volume > (ticket_source.total_volume - ticket_source.assigned_volume):
            raise ValidationError({"message": SafTicketAssignError.VOLUME_TOO_BIG})

        if assignment_period < ticket_source.delivery_period:
            raise ValidationError({"message": SafTicketAssignError.ASSIGNMENT_BEFORE_DELIVERY})

        try:
            with transaction.atomic():
                ticket = create_ticket_from_source(
                    ticket_source,
                    client_id=client_id,
                    volume=volume,
                    agreement_date=agreement_date,
                    agreement_reference=agreement_reference,
                    assignment_period=assignment_period,
                    free_field=free_field,
                )

                CarbureNotification.objects.create(
                    type=CarbureNotification.SAF_TICKET_RECEIVED,
                    dest_id=client_id,
                    send_by_email=False,
                    meta={
                        "supplier": ticket.supplier.name,
                        "ticket_id": ticket.id,
                        "year": ticket.year,
                    },
                )

                ticket_source.assigned_volume += ticket.volume
                ticket_source.save()

            return Response({}, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            raise ValidationError({"message": SafTicketAssignError.TICKET_CREATION_FAILED})

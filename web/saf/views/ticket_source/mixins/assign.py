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
from saf.services.is_shipping_route_available import is_shipping_route_available

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

        client = serializer.validated_data["client_id"]
        volume = serializer.validated_data["volume"]
        agreement_reference = serializer.validated_data.get("agreement_reference")
        agreement_date = serializer.validated_data.get("agreement_date")
        free_field = serializer.validated_data.get("free_field")
        assignment_period = serializer.validated_data["assignment_period"]
        reception_airport = serializer.validated_data.get("reception_airport")
        consumption_type = serializer.validated_data.get("consumption_type")
        shipping_method = serializer.validated_data.get("shipping_method")
        has_intermediary_depot = serializer.validated_data.get("has_intermediary_depot")

        pos_number = serializer.validated_data.get("pos_number")
        origin_lot_pos_number = ticket_source.origin_lot.pos_number if ticket_source.origin_lot else None

        if volume > (ticket_source.total_volume - ticket_source.assigned_volume):
            raise ValidationError({"message": SafTicketAssignError.VOLUME_TOO_BIG})

        if assignment_period < ticket_source.delivery_period:
            raise ValidationError({"message": SafTicketAssignError.ASSIGNMENT_BEFORE_DELIVERY})

        if pos_number and origin_lot_pos_number and pos_number != origin_lot_pos_number:
            raise ValidationError({"message": SafTicketAssignError.POS_NUMBER_MISMATCH})

        if not is_shipping_route_available(
            ticket_source.origin_lot_site, reception_airport, shipping_method, has_intermediary_depot
        ):
            raise ValidationError({"message": SafTicketAssignError.SHIPPING_ROUTE_NOT_REGISTERED})

        with transaction.atomic():
            ticket = create_ticket_from_source(
                ticket_source,
                client_id=client.id,
                volume=volume,
                agreement_date=agreement_date,
                agreement_reference=agreement_reference,
                assignment_period=assignment_period,
                free_field=free_field,
                reception_airport=reception_airport,
                consumption_type=consumption_type,
                shipping_method=shipping_method,
            )

            ticket_source.assigned_volume += ticket.volume
            ticket_source.save()

            # save pos_number on origin lot so it can be automatically reused on any other ticket based on it
            if ticket_source.origin_lot and origin_lot_pos_number != pos_number:
                ticket_source.origin_lot.pos_number = pos_number
                ticket_source.origin_lot.save()

            CarbureNotification.objects.create(
                type=CarbureNotification.SAF_TICKET_RECEIVED,
                dest_id=client.id,
                send_by_email=False,
                meta={
                    "supplier": ticket.supplier.name,
                    "ticket_id": ticket.id,
                    "year": ticket.year,
                },
            )

        return Response({}, status=status.HTTP_200_OK)

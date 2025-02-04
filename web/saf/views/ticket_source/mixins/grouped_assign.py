import traceback

from django.db import transaction
from django.db.models.aggregates import Max, Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.models import CarbureNotification
from saf.models import SafTicketSource, create_ticket_from_source
from saf.serializers import SafTicketSourceGroupAssignmentSerializer
from saf.serializers.schema import ErrorResponseSerializer

from .utils import SafTicketAssignError


class GroupAssignmentResponseSerializer(serializers.Serializer):
    assigned_tickets_count = serializers.IntegerField()


class GroupAssignActionMixin:
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
        responses={200: GroupAssignmentResponseSerializer, 400: ErrorResponseSerializer},
    )
    @action(
        methods=["post"],
        detail=False,
        url_path="group-assign",
        serializer_class=SafTicketSourceGroupAssignmentSerializer,
    )
    def grouped_assign(self, request, *args, **kwargs):
        entity_id = int(request.query_params.get("entity_id"))
        serializer = SafTicketSourceGroupAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket_sources_ids = serializer.validated_data["ticket_sources_ids"]
        client_id = serializer.validated_data["client_id"]
        volume = serializer.validated_data["volume"]
        agreement_reference = serializer.validated_data.get("agreement_reference")
        agreement_date = serializer.validated_data.get("agreement_date")
        free_field = serializer.validated_data.get("free_field")
        assignment_period = serializer.validated_data["assignment_period"]
        reception_airport = serializer.validated_data.get("reception_airport")
        consumption_type = serializer.validated_data.get("consumption_type")
        shipping_method = serializer.validated_data.get("shipping_method")

        ticket_sources = SafTicketSource.objects.filter(id__in=ticket_sources_ids, added_by_id=entity_id).order_by(
            "created_at"
        )

        if not ticket_sources:
            return Response(
                {"message": SafTicketAssignError.TICKET_SOURCE_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            total_volume_in_selection = ticket_sources.aggregate(Sum("total_volume"))["total_volume__sum"]
            assigned_volume_in_selection = ticket_sources.aggregate(Sum("assigned_volume"))["assigned_volume__sum"]
            if volume > (total_volume_in_selection - assigned_volume_in_selection):
                return Response(
                    {"message": SafTicketAssignError.VOLUME_TOO_BIG},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # use the most recent period of all the selected ticket sources to decide if the asked period is ok
            most_recent_period = ticket_sources.aggregate(Max("delivery_period"))["delivery_period__max"]
            if assignment_period < most_recent_period:
                return Response(
                    {"message": SafTicketAssignError.ASSIGNMENT_BEFORE_DELIVERY},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                assigned_tickets_count = 0
                remaining_volume_to_assign = volume

                for ticket_source in ticket_sources:
                    # create a ticket with a volume taking into account:
                    # - what's left in the ticket source
                    available_volume_in_source = ticket_source.total_volume - ticket_source.assigned_volume
                    # - and what's left in the amount asked by the user
                    ticket_volume = min(remaining_volume_to_assign, available_volume_in_source)

                    # do not
                    if ticket_volume <= 0:
                        break

                    ticket = create_ticket_from_source(
                        ticket_source,
                        client_id=client_id,
                        volume=ticket_volume,
                        agreement_date=agreement_date,
                        agreement_reference=agreement_reference,
                        assignment_period=assignment_period,
                        free_field=free_field,
                        reception_airport=reception_airport,
                        consumption_type=consumption_type,
                        shipping_method=shipping_method,
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

                    assigned_tickets_count += 1
                    ticket_source.assigned_volume += ticket.volume
                    remaining_volume_to_assign -= ticket.volume
                    ticket_source.save()

            return Response(
                {"assigned_tickets_count": assigned_tickets_count},
                status=status.HTTP_200_OK,
            )
        except Exception:
            traceback.print_exc()
            raise ValidationError({"message": SafTicketAssignError.TICKET_CREATION_FAILED})

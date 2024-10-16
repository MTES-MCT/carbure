import traceback

from django.db import transaction
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

from core.models import CarbureNotification
from saf.models import SafTicket, create_source_from_ticket


class SafTicketAcceptError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TICKET_ACCEPTANCE_FAILED = "TICKET_ACCEPTANCE_FAILED"
    TICKET_NOT_FOUND = "TICKET_NOT_FOUND"


class CreditTicketSourceSerializer(serializers.Serializer):
    ticket_id = serializers.IntegerField()
    entity_id = serializers.IntegerField()


class CreditActionMixin:
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
                "Example of credit response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["get"], detail=True, url_path="credit-source")
    def credit_source(self, request, id=None):
        entity_id = int(request.query_params.get("entity_id"))
        ticket = get_object_or_404(SafTicket, id=id, client_id=entity_id)

        try:
            with transaction.atomic():
                ticket.status = SafTicket.ACCEPTED
                ticket.save()

                create_source_from_ticket(ticket, entity_id)

                CarbureNotification.objects.create(
                    type=CarbureNotification.SAF_TICKET_ACCEPTED,
                    dest_id=ticket.supplier_id,
                    send_by_email=False,
                    meta={
                        "client": ticket.client.name,
                        "ticket_id": ticket.id,
                        "year": ticket.year,
                    },
                )

            return Response({"status": "success"})
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": SafTicketAcceptError.TICKET_ACCEPTANCE_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )

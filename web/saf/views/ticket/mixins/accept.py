import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import CarbureNotification
from saf.models import SafTicket, create_source_from_ticket
from saf.serializers.schema import CommentSerializer, ErrorResponseSerializer

from .utils import SafTicketError


class AcceptActionMixin:
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
        responses={200: OpenApiTypes.ANY, 400: ErrorResponseSerializer},
    )
    @action(methods=["post"], detail=True, serializer_class=CommentSerializer)
    def accept(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
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

            return Response({}, status=status.HTTP_200_OK)
        except Exception:
            traceback.print_exc()
            return Response(
                {"error": SafTicketError.TICKET_ACCEPTANCE_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )
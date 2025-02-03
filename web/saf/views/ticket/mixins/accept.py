import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import CarbureNotification
from saf.models import SafTicket
from saf.serializers.schema import ErrorResponseSerializer

from .utils import SafTicketError


class AcceptSerializer(serializers.Serializer):
    ets_status = serializers.ChoiceField(choices=SafTicket.ETS_STATUS)
    ets_declaration_date = serializers.DateField(required=False)


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
    @action(methods=["post"], detail=True, serializer_class=AcceptSerializer)
    def accept(self, request, id=None):
        entity_id = self.request.query_params.get("entity_id")
        ets_status = request.data.get("ets_status")
        ets_declaration_date = request.data.get("ets_declaration_date")

        ticket = get_object_or_404(SafTicket, id=id, client_id=entity_id)

        try:
            with transaction.atomic():
                ticket.status = SafTicket.ACCEPTED
                ticket.ets_status = ets_status
                ticket.ets_declaration_date = ets_declaration_date
                ticket.save()

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

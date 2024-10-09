import traceback

from django.db.models.expressions import F
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity
from saf.models import SafTicket, SafTicketSource
from saf.permissions import HasUserRights
from saf.serializers.schema import ErrorResponseSerializer


class ExtraError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"
    YEAR_LISTING_FAILED = "YEAR_LISTING_FAILED"


@extend_schema(
    parameters=[
        OpenApiParameter(
            "entity_id",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Entity ID",
            required=True,
        ),
        OpenApiParameter(
            "year",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Year",
            required=True,
        ),
    ],
    examples=[
        OpenApiExample(
            "Example of filters response.",
            value={"tickets_pending": 5, "tickets_accepted": 10, "...": "..."},
            request_only=False,
            response_only=True,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "oneOf": [
                {
                    "type": "object",
                    "properties": {"tickets_pending": {"type": "integer"}, "tickets_accepted": {"type": "integer"}},
                    "required": ["tickets_pending", "tickets_accepted"],
                },
                {
                    "type": "object",
                    "properties": {
                        "ticket_sources_available": {"type": "integer"},
                        "ticket_sources_history": {"type": "integer"},
                        "tickets_assigned": {"type": "integer"},
                        "tickets_assigned_pending": {"type": "integer"},
                        "tickets_assigned_accepted": {"type": "integer"},
                        "tickets_assigned_rejected": {"type": "integer"},
                        "tickets_received": {"type": "integer"},
                        "tickets_received_pending": {"type": "integer"},
                        "tickets_received_accepted": {"type": "integer"},
                    },
                    "required": [
                        "ticket_sources_available",
                        "ticket_sources_history",
                        "tickets_assigned",
                        "tickets_assigned_pending",
                        "tickets_assigned_accepted",
                        "tickets_assigned_rejected",
                        "tickets_received",
                        "tickets_received_pending",
                        "tickets_received_accepted",
                    ],
                },
            ],
        },
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, HasUserRights(None, [Entity.OPERATOR, Entity.AIRLINE])])
def get_snapshot(request, *args, **kwargs):
    entity_id = request.query_params.get("entity_id")
    year = request.query_params.get("year")

    entity = Entity.objects.get(id=entity_id)
    if not year:
        return Response({"message": ExtraError.MALFORMED_PARAMS}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if entity.entity_type == Entity.AIRLINE:
            tickets = SafTicket.objects.filter(year=year, client_id=entity_id)
            return Response(
                {
                    "tickets_pending": tickets.filter(status=SafTicket.PENDING).count(),
                    "tickets_accepted": tickets.filter(status=SafTicket.ACCEPTED).count(),
                },
                status=status.HTTP_200_OK,
            )
        sources = SafTicketSource.objects.filter(year=year, added_by_id=entity_id)
        tickets_assigned = SafTicket.objects.filter(year=year, supplier_id=entity_id)
        tickets_received = SafTicket.objects.filter(year=year, client_id=entity_id).exclude(status=SafTicket.REJECTED)
        return Response(
            {
                "ticket_sources_available": sources.filter(assigned_volume__lt=F("total_volume")).count(),
                "ticket_sources_history": sources.filter(assigned_volume=F("total_volume")).count(),
                "tickets_assigned": tickets_assigned.count(),
                "tickets_assigned_pending": tickets_assigned.filter(status=SafTicket.PENDING).count(),
                "tickets_assigned_accepted": tickets_assigned.filter(status=SafTicket.ACCEPTED).count(),
                "tickets_assigned_rejected": tickets_assigned.filter(status=SafTicket.REJECTED).count(),
                "tickets_received": tickets_received.count(),
                "tickets_received_pending": tickets_received.filter(status=SafTicket.PENDING).count(),
                "tickets_received_accepted": tickets_received.filter(status=SafTicket.ACCEPTED).count(),
            },
            status=status.HTTP_200_OK,
        )
    except Exception:
        traceback.print_exc()
        return Response({"message": ExtraError.SNAPSHOT_FAILED}, status=status.HTTP_400_BAD_REQUEST)

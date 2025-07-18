from xml.etree.ElementTree import ParseError

from django.db.models import F
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.models import Entity
from saf.models import SafTicket, SafTicketSource
from saf.permissions import HasAirlineRights, HasSafAdminRights, HasSafOperatorRights, HasSafTraderRights
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
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET"])
@permission_classes([HasAirlineRights | HasSafTraderRights | HasSafOperatorRights | HasSafAdminRights])
def get_snapshot(request, *args, **kwargs):
    entity = request.entity
    year = request.query_params.get("year")

    if not year:
        raise ParseError("MISSING_YEAR")

    tickets_assigned = SafTicket.objects.filter(year=year)
    tickets_received = SafTicket.objects.filter(year=year).exclude(status=SafTicket.REJECTED)
    ticket_sources = SafTicketSource.objects.filter(year=year)

    if entity.entity_type == Entity.AIRLINE:
        tickets_assigned = tickets_assigned.none()
        tickets_received = tickets_received.filter(client=entity)
        ticket_sources = ticket_sources.none()

    if entity.entity_type in (Entity.OPERATOR, Entity.SAF_TRADER):
        tickets_assigned = tickets_assigned.filter(supplier=entity)
        tickets_received = tickets_received.filter(client=entity)
        ticket_sources = ticket_sources.filter(added_by=entity)

    if entity.entity_type in (Entity.ADMIN, Entity.EXTERNAL_ADMIN):
        tickets_received = tickets_received.none()

    return Response(
        {
            "ticket_sources_available": ticket_sources.filter(assigned_volume__lt=F("total_volume")).count(),
            "ticket_sources_history": ticket_sources.filter(assigned_volume=F("total_volume")).count(),
            "tickets_assigned": tickets_assigned.count(),
            "tickets_assigned_pending": tickets_assigned.filter(status=SafTicket.PENDING).count(),
            "tickets_assigned_accepted": tickets_assigned.filter(status=SafTicket.ACCEPTED).count(),
            "tickets_assigned_rejected": tickets_assigned.filter(status=SafTicket.REJECTED).count(),
            "tickets_received": tickets_received.count(),
            "tickets_received_pending": tickets_received.filter(status=SafTicket.PENDING).count(),
            "tickets_received_accepted": tickets_received.filter(status=SafTicket.ACCEPTED).count(),
        }
    )

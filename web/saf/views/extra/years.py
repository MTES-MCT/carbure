from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
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
        )
    ],
    examples=[
        OpenApiExample(
            "Example of filters response.",
            value=[
                "2020",
                "2021",
                "2022",
                "2023",
                "2024",
            ],
            request_only=False,
            response_only=True,
        ),
    ],
    responses={200: {"type": "array", "items": {"type": "integer"}}, 400: ErrorResponseSerializer},
)
@api_view(["GET"])
@permission_classes([HasAirlineRights | HasSafTraderRights | HasSafOperatorRights | HasSafAdminRights])
def get_years(request, *args, **kwargs):
    entity = request.entity

    tickets = SafTicket.objects.all()
    ticket_sources = SafTicketSource.objects.all()

    if entity.entity_type == Entity.AIRLINE:
        tickets = tickets.filter(client=entity)
        ticket_sources = ticket_sources.none()

    if entity.entity_type in (Entity.OPERATOR, Entity.SAF_TRADER):
        tickets = tickets.filter(Q(client=entity) | Q(supplier=entity))
        ticket_sources = ticket_sources.filter(added_by=entity)

    ticket_source_years = ticket_sources.values_list("year", flat=True).distinct()
    ticket_years = tickets.values_list("year", flat=True).distinct()

    years = sorted(set(list(ticket_source_years) + list(ticket_years)))
    return Response(years)

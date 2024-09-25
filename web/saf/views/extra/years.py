import traceback

from django.db.models import Q
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
@permission_classes([IsAuthenticated, HasUserRights(None, [Entity.OPERATOR, Entity.AIRLINE])])
def get_years(request, *args, **kwargs):
    try:
        entity_id = request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        if entity.entity_type == Entity.AIRLINE:
            ticket_years = SafTicket.objects.filter(client_id=entity_id).values_list("year", flat=True).distinct()
            years = sorted(set(ticket_years))
        else:
            ticket_source_years = (
                SafTicketSource.objects.filter(added_by_id=entity_id).values_list("year", flat=True).distinct()
            )
            client_or_supplier = Q(supplier_id=entity_id) | Q(client_id=entity_id)
            ticket_years = SafTicket.objects.filter(client_or_supplier).values_list("year", flat=True).distinct()
            years = sorted(set(list(ticket_source_years) + list(ticket_years)))
        return Response(years, status=status.HTTP_200_OK)
    except Exception:
        traceback.print_exc()
        return Response(
            {"message": ExtraError.YEAR_LISTING_FAILED},
            status=status.HTTP_400_BAD_REQUEST,
        )

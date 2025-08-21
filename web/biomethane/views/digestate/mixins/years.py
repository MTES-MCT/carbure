from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from core.models import Entity
from core.permissions import HasUserRights


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
                2020,
                2021,
                2022,
                2023,
                2024,
            ],
            request_only=False,
            response_only=True,
        ),
    ],
    responses={200: {"type": "array", "items": {"type": "integer"}}},
)
@api_view(["GET"])
@permission_classes([HasUserRights(entity_type=[Entity.BIOMETHANE_PRODUCER])])
def get_years(request, *args, **kwargs):
    entity = request.entity

    years = BiomethaneDigestate.objects.filter(producer=entity).values_list("year", flat=True).distinct()

    return Response(years)

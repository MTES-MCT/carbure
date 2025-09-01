from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models.biomethane_energy import BiomethaneEnergy


class YearsActionMixin:
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
    @action(
        detail=False,
        methods=["get"],
        url_path="years",
    )
    def get_years(self, request, *args, **kwargs):
        entity = request.entity
        years = BiomethaneEnergy.objects.filter(producer=entity).values_list("year", flat=True).distinct()
        return Response(sorted(years))

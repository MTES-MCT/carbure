from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.utils import get_declaration_period


class ValidateActionMixin:
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
        request=None,
        responses={
            200: None,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="validate",
    )
    def validate_energy(self, request, *args, **kwargs):
        try:
            year = get_declaration_period()
            energy = BiomethaneEnergy.objects.get(producer=request.entity, year=year)

            energy.status = BiomethaneEnergy.VALIDATED
            energy.save(update_fields=["status"])

            return Response(status=status.HTTP_200_OK)
        except BiomethaneEnergy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

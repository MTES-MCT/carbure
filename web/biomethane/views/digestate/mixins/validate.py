from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from biomethane.models.biomethane_digestate import BiomethaneDigestate
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
    def validate_digestate(self, request, *args, **kwargs):
        try:
            year = get_declaration_period()
            digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=year)

            digestate.status = BiomethaneDigestate.VALIDATED
            digestate.save(update_fields=["status"])

            return Response(status=status.HTTP_200_OK)
        except BiomethaneDigestate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

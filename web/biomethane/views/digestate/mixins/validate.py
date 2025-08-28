from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.utils import get_declaration_period
from core.models import Entity, UserRights
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
    request=None,
    responses={
        200: None,
    },
)
@api_view(["POST"])
@permission_classes([HasUserRights(role=UserRights.RW, entity_type=[Entity.BIOMETHANE_PRODUCER])])
def validate(request, *args, **kwargs):
    try:
        declaration_period = get_declaration_period()
        year = declaration_period["declaration_year"]
        digestate = BiomethaneDigestate.objects.get(producer=request.entity, year=year)

        digestate.status = BiomethaneDigestate.VALIDATED
        digestate.save()

        return Response(status=status.HTTP_200_OK)
    except BiomethaneDigestate.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

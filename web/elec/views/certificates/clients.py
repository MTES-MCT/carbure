from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity
from core.serializers import EntityPreviewSerializer
from elec.permissions import HasCpoUserRights


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            description="Entity querying the endpoint",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="query",
            description="Search within the field `name`",
            required=False,
            type=str,
        ),
    ],
    responses=EntityPreviewSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated & HasCpoUserRights])
def get_clients(request, *args, **kwargs):
    query = request.query_params.get("query")
    entities = Entity.objects.filter(entity_type=Entity.OPERATOR, has_elec=True, name__icontains=query).order_by("name")
    serializer = EntityPreviewSerializer(entities, many=True)
    return Response(serializer.data)

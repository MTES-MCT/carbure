from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity
from resources.serializers import EntityResourceSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the field `name`",
            required=False,
            type=str,
        )
    ],
    responses=EntityResourceSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_traders(request, *args, **kwargs):
    query = request.query_params.get("query")

    entities = Entity.objects.filter(entity_type=Entity.TRADER).order_by("name")

    if query:
        entities = entities.filter(name__icontains=query)

    serializer = EntityResourceSerializer(entities, many=True)
    return Response(serializer.data)

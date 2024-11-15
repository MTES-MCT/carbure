from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity
from resources.serializers import EntitySerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the field `name`",
            required=False,
            type=str,
        )
    ],
    responses=EntitySerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_entities(request, *args, **kwargs):
    query = request.query_params.get("query")

    entities = Entity.objects.all().order_by("name")

    if query:
        entities = entities.filter(name__icontains=query)

    serializer = EntitySerializer(entities, many=True)
    return Response(serializer.data)

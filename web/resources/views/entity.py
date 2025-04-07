from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity
from core.serializers import EntityPreviewSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the field `name`",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="is_enabled",
            description="Only show enabled entities",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="entity_type",
            description="Only keep specific entity types",
            required=False,
            type=str,
            many=True,
        ),
        OpenApiParameter(
            name="is_tiruert_liable",
            description="Only show liable entities",
            required=False,
            type=bool,
        ),
    ],
    responses=EntityPreviewSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_entities(request, *args, **kwargs):
    query = request.query_params.get("query")
    is_enabled = request.query_params.get("is_enabled") == "true"
    entity_type = request.query_params.getlist("entity_type")
    is_tiruert_liable = request.query_params.get("is_tiruert_liable") == "true"

    entities = Entity.objects.all().order_by("name")

    if query:
        entities = entities.filter(name__icontains=query)
    if entity_type:
        entities = entities.filter(entity_type__in=entity_type)
    if is_enabled:
        entities = entities.filter(is_enabled=True)
    if is_tiruert_liable:
        entities = entities.filter(is_tiruert_liable=True)

    serializer = EntityPreviewSerializer(entities, many=True)
    return Response(serializer.data)

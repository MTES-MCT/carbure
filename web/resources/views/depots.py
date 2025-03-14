from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers import DepotSerializer
from transactions.models.depot import Depot


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `name`, `name_en` and `code_pays`",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="public_only",
            description="Public Only",
            required=False,
            type=bool,
        ),
    ],
    responses=DepotSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_depots(request, *args, **kwargs):
    query = request.query_params.get("query")
    public_only = request.query_params.get("public_only", False)
    only_enabled = request.query_params.get("only_enabled", True)

    dsites = Depot.objects.all().order_by("name")
    if only_enabled:
        dsites = dsites.filter(is_enabled=True)
    if public_only:
        dsites = dsites.filter(private=False)
    if query:
        dsites = dsites.filter(Q(name__icontains=query) | Q(customs_id__icontains=query) | Q(city__icontains=query))

    serializer = DepotSerializer(dsites, many=True)

    return Response(serializer.data)

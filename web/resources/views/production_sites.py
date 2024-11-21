from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers import ProductionSiteSerializer
from producers.models import ProductionSite


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the field `name`",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="producer_id",
            description="Search within the field `producer_id`",
            required=False,
            type=int,
        ),
    ],
    responses=ProductionSiteSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_production_sites(request, *args, **kwargs):
    query = request.query_params.get("query")
    pid = request.query_params.get("producer_id", False)

    psites = ProductionSite.objects.select_related("country", "producer").all().order_by("name")

    if query:
        psites = psites.filter(name__icontains=query)

    if pid:
        psites = psites.filter(producer__id=pid)

    serializer = ProductionSiteSerializer(psites, many=True)
    return Response(serializer.data)

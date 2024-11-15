from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import MatierePremiere
from resources.serializers import MatierePremiereSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `name`, `name_en` and `code`",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="double_count_only",
            description="Double compte only",
            required=False,
            type=bool,
        ),
    ],
    responses=MatierePremiereSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feedstocks(request, *args, **kwargs):
    query = request.query_params.get("query")
    double_count_only = request.query_params.get("double_count_only", False)

    mps = MatierePremiere.objects.filter(is_displayed=True).order_by("name")
    if double_count_only == "true":
        mps = mps.filter(is_double_compte=True)
    if query:
        mps = mps.filter(Q(name__icontains=query) | Q(name_en__icontains=query) | Q(code__icontains=query))

    serializer = MatierePremiereSerializer(mps, many=True)
    return Response(serializer.data)

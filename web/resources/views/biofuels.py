from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Biocarburant
from doublecount.serializers import BiofuelSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `name`, `name_en`, and `code`",
            required=False,
            type=str,
        ),
    ],
    responses=BiofuelSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_biofuels(request, *args, **kwargs):
    query = request.query_params.get("query")

    bcs = Biocarburant.objects.filter(is_displayed=True).order_by("name")
    if query:
        bcs = bcs.filter(Q(name__icontains=query) | Q(name_en__icontains=query) | Q(code__icontains=query))
    serializer = BiofuelSerializer(bcs, many=True)
    return Response(serializer.data)

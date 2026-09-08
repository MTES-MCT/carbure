from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.permissions import IsVerified
from traceability.models import Material
from traceability.serializers import MaterialSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `name` and `code`",
            required=False,
            type=str,
        ),
    ],
    responses=MaterialSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsVerified])
def get_materials(request, *args, **kwargs):
    query = request.query_params.get("query")

    materials = Material.objects.all().order_by("name")
    if query:
        materials = materials.filter(Q(name__icontains=query) | Q(code__icontains=query))

    return Response(MaterialSerializer(materials, many=True).data)

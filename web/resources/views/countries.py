from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Pays
from doublecount.serializers import CountrySerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `name`, `name_en` and `code_pays`",
            required=False,
            type=str,
        ),
    ],
    responses=CountrySerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_countries(request, *args, **kwargs):
    query = request.query_params.get("query")

    countries = Pays.objects.all().order_by("name")
    if query:
        countries = countries.filter(Q(name__icontains=query) | Q(name_en__icontains=query) | Q(code_pays__icontains=query))
    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data)

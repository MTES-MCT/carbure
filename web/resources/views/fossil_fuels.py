from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tiruert.models import FossilFuel


class FossilFuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FossilFuel
        fields = [
            "id",
            "label",
            "nomenclature",
        ]


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `label` and `nomenclature`",
            required=False,
            type=str,
        ),
    ],
    responses=FossilFuelSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_fossil_fuels(request, *args, **kwargs):
    query = request.query_params.get("query")

    fossil_fuels = FossilFuel.objects.all().order_by("label")
    if query:
        fossil_fuels = fossil_fuels.filter(Q(label__icontains=query) | Q(nomenclature__icontains=query))

    serializer = FossilFuelSerializer(fossil_fuels, many=True)
    return Response(serializer.data)

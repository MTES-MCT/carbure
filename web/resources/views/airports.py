from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers import AirportSerializer
from core.utils import extract_enum
from saf.models.saf_logistics import SafLogistics
from transactions.models.airport import Airport


class AirportQueryParamsSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    public_only = serializers.BooleanField(required=False, default=False)
    origin_depot_id = serializers.IntegerField(required=False)
    shipping_method = serializers.ChoiceField(required=False, choices=extract_enum(SafLogistics, "shipping_method"))
    has_intermediary_depot = serializers.BooleanField(required=False, default=False)


@extend_schema(
    parameters=[AirportQueryParamsSerializer],
    responses=AirportSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_airports(request, *args, **kwargs):
    serializer = AirportQueryParamsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    public_only = serializer.validated_data.get("public_only", False)
    query = serializer.validated_data.get("query", None)
    origin_depot_id = serializer.validated_data.get("origin_depot_id", None)
    shipping_method = serializer.validated_data.get("shipping_method", None)
    has_intermediary_depot = serializer.validated_data.get("has_intermediary_depot", False)

    sites = Airport.objects.all().order_by("name").filter(is_enabled=True)

    if public_only:
        sites = sites.filter(private=False)
    if query:
        sites = sites.filter(Q(name__icontains=query) | Q(customs_id__icontains=query) | Q(city__icontains=query))
    if origin_depot_id and shipping_method:
        if SafLogistics.objects.filter(
            origin_depot_id=origin_depot_id,
            shipping_method=shipping_method,
            has_intermediary_depot=has_intermediary_depot,
        ).exists():
            sites = sites.filter(
                airport_from_depot_routes__origin_depot_id=origin_depot_id,
                airport_from_depot_routes__shipping_method=shipping_method,
                airport_from_depot_routes__has_intermediary_depot=has_intermediary_depot,
            )

    serializer = AirportSerializer(sites, many=True)

    return Response(serializer.data)

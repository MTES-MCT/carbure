from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneSupplyPlanFilter, BiomethaneSupplyPlanYearsFilter
from biomethane.models import BiomethaneSupplyPlan
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import BiomethaneSupplyPlanSerializer

from .mixins import YearsActionMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneSupplyPlanViewSet(GenericViewSet, YearsActionMixin):
    queryset = BiomethaneSupplyPlan.objects.all()
    filterset_class = BiomethaneSupplyPlanFilter
    serializer_class = BiomethaneSupplyPlanSerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions([], self.action)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "get_years":
            return BiomethaneSupplyPlanYearsFilter(self.request.GET, queryset=queryset).qs
        return self.filter_queryset(queryset)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Declaration year.",
                required=True,
            ),
        ],
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=BiomethaneSupplyPlanSerializer,
                description="Supply plan details for the entity",
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Supply plan not found for this entity."),
        },
        description="Retrieve the supply plan for the current entity and year. Returns a single production unit object.",
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            supply_plan = self.get_queryset().get()
            data = self.get_serializer(supply_plan, many=False).data
            return Response(data)
        except BiomethaneSupplyPlan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

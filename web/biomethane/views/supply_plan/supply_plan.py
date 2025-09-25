from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import GenericViewSet

from biomethane.filters import BiomethaneSupplyPlanYearsFilter
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
    serializer_class = BiomethaneSupplyPlanSerializer
    filterset_class = BiomethaneSupplyPlanYearsFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions([], self.action)

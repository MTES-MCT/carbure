from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.models import BiomethaneSupplyInput, BiomethaneSupplyPlan
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers.supply_plan.supply_input import (
    BiomethaneSupplyInputCreateSerializer,
    BiomethaneSupplyInputSerializer,
)
from biomethane.utils import get_declaration_period


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
class BiomethaneSupplyInputViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = BiomethaneSupplyInput.objects.all()
    serializer_class = BiomethaneSupplyInputSerializer
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["create", "update", "partial_update"], self.action)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BiomethaneSupplyInputCreateSerializer
        return BiomethaneSupplyInputSerializer

    def perform_create(self, serializer):
        entity = self.request.entity
        year = get_declaration_period()

        # Get or create the supply plan for the entity and year
        supply_plan, created = BiomethaneSupplyPlan.objects.get_or_create(
            producer=entity,
            year=year,
            defaults={},
        )

        serializer.save(supply_plan=supply_plan)

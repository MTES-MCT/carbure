from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.mixins import EntityProducerFilter
from biomethane.models import BiomethaneSupplyPlan
from biomethane.permissions import get_biomethane_permissions
from biomethane.serializers import BiomethaneSupplyPlanSerializer
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from biomethane.views.mixins import YearsActionMixin

from .mixins import ExcelImportActionMixin


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
class BiomethaneSupplyPlanViewSet(GenericViewSet, YearsActionMixin, ExcelImportActionMixin):
    queryset = BiomethaneSupplyPlan.objects.all()
    serializer_class = BiomethaneSupplyPlanSerializer
    filterset_class = EntityProducerFilter
    pagination_class = None

    def get_permissions(self):
        return get_biomethane_permissions(["import_supply_plan_from_excel"], self.action)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_queryset(self):
        if self.action == "import_supply_plan_from_excel":
            entity = getattr(self.request, "entity", None)
            year = BiomethaneAnnualDeclarationService.get_declaration_period(entity)
            try:
                return super().get_queryset().get(producer=self.request.entity, year=year)
            except BiomethaneSupplyPlan.DoesNotExist:
                return None
        return super().get_queryset()

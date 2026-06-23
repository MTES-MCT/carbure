from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.admin.annual_declaration import BiomethaneAdminAnnualDeclarationFilter
from biomethane.permissions import CanAccessAdminModule
from biomethane.serializers.admin.annual_declaration import BiomethaneAdminAnnualDeclarationSerializer
from biomethane.services.admin.dashboard import BiomethaneAdminDashboardService
from core.filters import FiltersActionFactory
from core.models import Entity


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class BiomethaneAdminAnnualDeclarationViewSet(GenericViewSet, ListModelMixin, FiltersActionFactory()):
    """Liste des déclarations annuelles des producteurs de biométhane pour l'année courante (vue DREAL)."""

    queryset = Entity.objects.filter(entity_type=Entity.BIOMETHANE_PRODUCER)
    filterset_class = BiomethaneAdminAnnualDeclarationFilter
    permission_classes = [CanAccessAdminModule]
    serializer_class = BiomethaneAdminAnnualDeclarationSerializer

    def get_queryset(self):
        year = self.request.query_params.get("year")
        return BiomethaneAdminDashboardService.get_dashboard_queryset(
            self.request.entity,
            int(year) if year is not None else None,
        )

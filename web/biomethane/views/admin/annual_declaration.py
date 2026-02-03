from django.db.models import Case, Q, Value, When
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from biomethane.filters.admin.annual_declaration import BiomethaneAdminAnnualDeclarationFilter
from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.permissions import HasDrealRights
from biomethane.serializers.admin.annual_declaration import BiomethaneAdminAnnualDeclarationSerializer
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.filters import FiltersActionFactory


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

    queryset = BiomethaneAnnualDeclaration.objects.all()
    filterset_class = BiomethaneAdminAnnualDeclarationFilter
    permission_classes = [HasDrealRights]
    serializer_class = BiomethaneAdminAnnualDeclarationSerializer

    def get_queryset(self):
        entity = self.request.entity
        year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        accessible_dept_codes = list(entity.get_accessible_departments().values_list("code_dept", flat=True))
        declarations = (
            BiomethaneAnnualDeclaration.objects.filter(year=year)
            .select_related(
                "producer__biomethane_contract",
                "producer__biomethane_production_unit__department",
            )
            .filter(
                Q(producer__biomethane_production_unit__department__code_dept__in=accessible_dept_codes)
                | Q(producer__registered_zipcode__in=accessible_dept_codes)
            )
            # Return declarations with status in progress first, then others
            # This is useful when the declaration period is terminated, DREAL wants to see the declarations not validated
            .annotate(
                priority=Case(
                    When(status=BiomethaneAnnualDeclaration.IN_PROGRESS, then=Value(1)),
                    default=Value(0),
                )
            )
            .order_by("-priority", "producer__name")
        )

        return declarations

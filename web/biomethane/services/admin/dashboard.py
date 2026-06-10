from django.db.models import Case, CharField, F, OuterRef, Subquery, Value, When
from django.db.models.functions import Coalesce

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity

# First = highest priority in the list (DECLARED uses default=0).
DECLARATION_STATUS_ORDER = (
    BiomethaneAnnualDeclaration.NOT_STARTED,
    BiomethaneAnnualDeclaration.OVERDUE,
    BiomethaneAnnualDeclaration.IN_PROGRESS,
)


class BiomethaneAdminDashboardService:
    @staticmethod
    def get_dashboard_queryset(entity):
        """
        Returns biomethane producers visible to the admin entity, including those
        without an annual declaration for the current year (NOT_STARTED status).
        """
        year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
        declaration_subquery = BiomethaneAnnualDeclaration.objects.filter(
            producer=OuterRef("pk"),
            year=year,
        )
        q = (
            entity.get_allowed_entities()
            .filter(entity_type=Entity.BIOMETHANE_PRODUCER)
            .select_related(
                "biomethane_contract",
                "biomethane_production_unit__department",
            )
            .annotate(
                _declaration_status=Subquery(declaration_subquery.values("status")[:1]),
                _declaration_year=Subquery(declaration_subquery.values("year")[:1]),
                year=Coalesce(F("_declaration_year"), Value(year)),
            )
            .annotate(
                _computed_status=BiomethaneAnnualDeclarationService.get_declaration_status_annotation("_declaration_status"),
                _department_code=Coalesce(
                    F("biomethane_production_unit__department__code_dept"),
                    F("registered_zipcode"),
                    output_field=CharField(),
                ),
            )
            .annotate(
                _priority=Case(
                    *[
                        When(
                            _computed_status=status,
                            then=Value(len(DECLARATION_STATUS_ORDER) - index),
                        )
                        for index, status in enumerate(DECLARATION_STATUS_ORDER)
                    ],
                    default=Value(0),
                ),
            )
            .order_by("-_priority", "name")
        )
        return q

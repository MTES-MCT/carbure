from datetime import date

from django.db.models import Case, CharField, F, OuterRef, Q, Subquery, Value, When
from django.db.models.functions import Coalesce

from biomethane.models import BiomethaneAnnualDeclaration
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity


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
        is_overdue = date.today() > BiomethaneAnnualDeclarationService.OVERDUE_DATE

        status_cases = [
            When(_declaration_status__isnull=True, then=Value(BiomethaneAnnualDeclaration.NOT_STARTED)),
        ]
        if is_overdue:
            status_cases.append(
                When(
                    ~Q(_declaration_status=BiomethaneAnnualDeclaration.DECLARED),
                    then=Value(BiomethaneAnnualDeclaration.OVERDUE),
                )
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
            )
            .annotate(
                _computed_status=Case(
                    *status_cases,
                    default=F("_declaration_status"),
                    output_field=CharField(),
                ),
                _department_code=Coalesce(
                    F("biomethane_production_unit__department__code_dept"),
                    F("registered_zipcode"),
                    output_field=CharField(),
                ),
            )
            .annotate(
                _priority=Case(
                    When(
                        _computed_status=BiomethaneAnnualDeclaration.NOT_STARTED,
                        then=Value(3),
                    ),
                    When(
                        _computed_status=BiomethaneAnnualDeclaration.OVERDUE,
                        then=Value(2),
                    ),
                    When(
                        _computed_status=BiomethaneAnnualDeclaration.IN_PROGRESS,
                        then=Value(1),
                    ),
                    default=Value(0),
                ),
            )
            .order_by("-_priority", "name")
        )
        return q

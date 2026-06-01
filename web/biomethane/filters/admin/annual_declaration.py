from django_filters import AllValuesMultipleFilter, FilterSet, MultipleChoiceFilter

from biomethane.models.biomethane_annual_declaration import BiomethaneAnnualDeclaration
from biomethane.models.biomethane_contract import BiomethaneContract
from core.models import Entity


class BiomethaneAdminAnnualDeclarationFilter(FilterSet):
    tariff_reference = MultipleChoiceFilter(
        field_name="biomethane_contract__tariff_reference",
        choices=BiomethaneContract.TARIFF_REFERENCE_CHOICES,
    )

    department = AllValuesMultipleFilter(field_name="biomethane_production_unit__department__code_dept")
    status = MultipleChoiceFilter(
        field_name="_computed_status",
        choices=BiomethaneAnnualDeclaration.ADMIN_DASHBOARD_STATUS_CHOICES,
    )

    class Meta:
        model = Entity
        fields = []

from django_filters import AllValuesMultipleFilter, FilterSet, MultipleChoiceFilter

from biomethane.models.biomethane_annual_declaration import BiomethaneAnnualDeclaration
from biomethane.models.biomethane_contract import BiomethaneContract


class BiomethaneAdminAnnualDeclarationFilter(FilterSet):
    tariff_reference = MultipleChoiceFilter(
        field_name="producer__biomethane_contract__tariff_reference", choices=BiomethaneContract.TARIFF_REFERENCE_CHOICES
    )

    department = AllValuesMultipleFilter(field_name="producer__biomethane_production_unit__department__code_dept")
    status = MultipleChoiceFilter(choices=BiomethaneAnnualDeclaration.DECLARATION_STATUS)

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["tariff_reference", "department", "status"]

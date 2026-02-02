from django_filters import AllValuesMultipleFilter, FilterSet, MultipleChoiceFilter
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import ChoiceField

from biomethane.models.biomethane_annual_declaration import BiomethaneAnnualDeclaration
from biomethane.models.biomethane_contract import BiomethaneContract


class BiomethaneAdminAnnualDeclarationFilter(FilterSet):
    tariff_reference = extend_schema_field(ChoiceField(choices=BiomethaneContract.TARIFF_REFERENCE_CHOICES))(
        AllValuesMultipleFilter(
            field_name="producer__biomethane_contract__tariff_reference",
        )
    )

    department = AllValuesMultipleFilter(field_name="producer__biomethane_production_unit__department__code_dept")
    status = MultipleChoiceFilter(choices=BiomethaneAnnualDeclaration.DECLARATION_STATUS)

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["tariff_reference", "department", "status"]

from django_filters import FilterSet, NumberFilter

from biomethane.models import BiomethaneAnnualDeclaration


class BiomethaneProviderDeclarationFilter(FilterSet):
    year = NumberFilter(field_name="year", lookup_expr="exact", required=True)

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["year"]

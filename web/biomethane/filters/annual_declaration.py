from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneAnnualDeclaration


class BiomethaneAnnualDeclarationFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact")

    class Meta:
        model = BiomethaneAnnualDeclaration
        fields = ["entity_id"]

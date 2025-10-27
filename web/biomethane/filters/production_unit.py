from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneProductionUnit


class BiomethaneProductionUnitFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact")

    class Meta:
        model = BiomethaneProductionUnit
        fields = ["entity_id"]

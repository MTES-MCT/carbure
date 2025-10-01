from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneContract


class BiomethaneContractFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact")

    class Meta:
        model = BiomethaneContract
        fields = ["entity_id"]

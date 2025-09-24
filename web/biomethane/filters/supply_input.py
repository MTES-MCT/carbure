from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneSupplyInput


class BaseBiomethaneSupplyInputFilter(FilterSet):
    entity_id = CharFilter(field_name="supply_plan__producer__id", lookup_expr="exact", required=True)
    type = CharFilter(field_name="input_type", lookup_expr="exact", required=False)
    source = CharFilter(field_name="source", lookup_expr="exact", required=False)
    category = CharFilter(field_name="input_category", lookup_expr="exact", required=False)


class BiomethaneSupplyInputFilter(BaseBiomethaneSupplyInputFilter):
    year = CharFilter(field_name="supply_plan__year", lookup_expr="exact", required=True)

    class Meta:
        model = BiomethaneSupplyInput
        fields = ["entity_id", "year", "type", "source", "category"]


class BiomethaneSupplyInputCreateFilter(BaseBiomethaneSupplyInputFilter):
    class Meta:
        model = BiomethaneSupplyInput
        fields = ["entity_id"]

from django_filters import AllValuesMultipleFilter, CharFilter, FilterSet, MultipleChoiceFilter, NumberFilter

from biomethane.models import BiomethaneSupplyInput


class BaseBiomethaneSupplyInputFilter(FilterSet):
    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(field_name="supply_plan__producer__id", lookup_expr="exact")
    feedstock = AllValuesMultipleFilter(field_name="feedstock__name", lookup_expr="exact", required=False)
    source = MultipleChoiceFilter(field_name="source", choices=BiomethaneSupplyInput.SOURCE_CHOICES, required=False)

    def filter_by_entity(self, queryset, name, value):
        """
        Filter by entity_id:
        - If producer_id is provided (DREAL case), ignore entity_id for the producer filter
        - Otherwise (Producer case), filter by energy__producer_id = entity_id
        """
        if "producer_id" in self.data:
            # DREAL case: ignore entity_id for filtering, entity_id is just for permissions
            return queryset
        else:
            # Producer case
            return queryset.filter(supply_plan__producer__id=value)


class BiomethaneSupplyInputFilter(BaseBiomethaneSupplyInputFilter):
    year = NumberFilter(field_name="supply_plan__year", lookup_expr="exact", required=True)

    class Meta:
        model = BiomethaneSupplyInput
        fields = ["entity_id", "producer_id", "year", "feedstock", "source"]


class BiomethaneSupplyInputCreateFilter(BiomethaneSupplyInputFilter):
    class Meta:
        model = BiomethaneSupplyInput
        fields = ["entity_id", "year"]

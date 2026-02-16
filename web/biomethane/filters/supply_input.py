from django_filters import AllValuesMultipleFilter, CharFilter, FilterSet, MultipleChoiceFilter, NumberFilter

from biomethane.models import BiomethaneSupplyInput
from core.models import ExternalAdminRights


class BaseBiomethaneSupplyInputFilter(FilterSet):
    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(field_name="supply_plan__producer__id", lookup_expr="exact")
    input_name = AllValuesMultipleFilter(field_name="input_name__name", lookup_expr="exact", required=False)
    source = MultipleChoiceFilter(field_name="source", choices=BiomethaneSupplyInput.SOURCE_CHOICES, required=False)
    department = AllValuesMultipleFilter(field_name="origin_department", lookup_expr="exact", required=False)

    # Filter used for admin supply inputs page
    producer_name = AllValuesMultipleFilter(field_name="supply_plan__producer__name", lookup_expr="exact", required=False)

    def filter_by_entity(self, queryset, name, value):
        """
        Filter by entity_id:
        - If entity is a DREAL, two cases :
            - If producer_id is provided, do not use entity_id
            - Otherwise, filter by the entities allowed by the DREAL
        - Otherwise (Producer case), filter by supply_plan__producer_id = entity_id
        """

        entity = getattr(self.request, "entity", None)

        if entity and entity.has_external_admin_right(ExternalAdminRights.DREAL):
            if "producer_id" in self.data:
                return queryset
            else:
                allowed_entities = entity.get_allowed_entities().values_list("id", flat=True)
                return queryset.filter(supply_plan__producer_id__in=allowed_entities)

        # Producer case
        return queryset.filter(supply_plan__producer__id=value)


class BiomethaneSupplyInputFilter(BaseBiomethaneSupplyInputFilter):
    year = NumberFilter(field_name="supply_plan__year", lookup_expr="exact", required=True)

    class Meta:
        model = BiomethaneSupplyInput
        fields = ["entity_id", "producer_id", "year", "input_name", "source", "producer_name"]


class BiomethaneSupplyInputCreateFilter(BiomethaneSupplyInputFilter):
    class Meta:
        model = BiomethaneSupplyInput
        fields = ["entity_id", "year"]

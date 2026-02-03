from django_filters import CharFilter, FilterSet


class EntityCreatedByFilter(FilterSet):
    """
    FilterSet for models inheriting from Site (using created_by instead of producer).
    Used specifically for BiomethaneProductionUnit.

    Filter logic:
    - Producer: ?entity_id=123 → filters on created_by__id=123
    - DREAL: ?entity_id=456&producer_id=789 → filters on created_by__id=789
    """

    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(field_name="created_by__id", lookup_expr="exact")

    def filter_by_entity(self, queryset, name, value):
        """
        Filter by entity_id:
        - If producer_id is provided (DREAL case), ignore entity_id for the producer filter
        - Otherwise (Producer case), filter by created_by__id = entity_id
        """
        if "producer_id" in self.data:
            # DREAL case: ignore entity_id for filtering, entity_id is just for permissions
            return queryset
        else:
            # Producer case
            return queryset.filter(created_by__id=value)

    class Meta:
        fields = ["entity_id", "producer_id"]

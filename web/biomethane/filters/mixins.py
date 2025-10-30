from django_filters import CharFilter, FilterSet


class EntityProducerFilter(FilterSet):
    """
    Generic FilterSet for biomethane models with producer field.
    Can be used directly without subclassing if no additional filters needed.

    Usage in ViewSet:
        filterset_class = EntityProducerFilter
        queryset = BiomethaneEnergy.objects.all()

    Filter logic:
    - Producer: ?entity_id=123 → filters on producer__id=123
    - DREAL: ?entity_id=456&producer_id=789 → filters on producer__id=789
    """

    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(field_name="producer__id", lookup_expr="exact")

    def filter_by_entity(self, queryset, name, value):
        """
        Filter by entity_id:
        - If producer_id is provided (DREAL case), ignore entity_id for the producer filter
        - Otherwise (Producer case), filter by producer__id = entity_id
        """
        if "producer_id" in self.data:
            # DREAL case: ignore entity_id for filtering, entity_id is just for permissions
            return queryset
        else:
            # Producer case
            return queryset.filter(producer__id=value)

    class Meta:
        fields = ["entity_id", "producer_id"]


class EntityProducerYearFilter(EntityProducerFilter):
    year = CharFilter(field_name="year", lookup_expr="exact")

    class Meta:
        fields = ["entity_id", "producer_id", "year"]

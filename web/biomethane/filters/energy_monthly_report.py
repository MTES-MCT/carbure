from django_filters import CharFilter, FilterSet, NumberFilter


class BiomethaneEnergyMonthlyReportFilter(FilterSet):
    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(field_name="energy__producer_id", lookup_expr="exact")

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
            return queryset.filter(energy__producer_id=value)

    class Meta:
        fields = ["entity_id", "producer_id"]


class BiomethaneEnergyMonthlyReportYearFilter(BiomethaneEnergyMonthlyReportFilter):
    year = NumberFilter(field_name="energy__year", lookup_expr="exact", required=True)

    class Meta:
        fields = ["entity_id", "producer_id", "year"]

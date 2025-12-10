from django_filters import CharFilter, FilterSet, NumberFilter


class MacFilter(FilterSet):
    entity_id = CharFilter(field_name="operator_id", lookup_expr="exact")
    year = NumberFilter(field_name="year", lookup_expr="exact")

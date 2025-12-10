from django_filters import FilterSet, NumberFilter


class ObjectiveFilter(FilterSet):
    year = NumberFilter(field_name="year", lookup_expr="exact")

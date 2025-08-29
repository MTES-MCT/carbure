from django_filters import CharFilter, FilterSet


class BiomethaneDigestateFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact")

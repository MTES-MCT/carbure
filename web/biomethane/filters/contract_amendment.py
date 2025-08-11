from django_filters import CharFilter, FilterSet


class BiomethaneContractAmendmentFilter(FilterSet):
    entity_id = CharFilter(field_name="contract__entity_id", lookup_expr="exact")

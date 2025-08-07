from django_filters import CharFilter, FilterSet


class BiomethaneEntityConfigContractAmendmentFilter(FilterSet):
    entity_id = CharFilter(field_name="contract", lookup_expr="exact")

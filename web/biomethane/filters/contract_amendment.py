from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneContractAmendment


class BiomethaneContractAmendmentFilter(FilterSet):
    entity_id = CharFilter(field_name="contract__producer_id", lookup_expr="exact")

    class Meta:
        model = BiomethaneContractAmendment
        fields = ["entity_id"]

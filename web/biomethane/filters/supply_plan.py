from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneSupplyPlan


class BiomethaneSupplyPlanYearsFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact", required=True)

    class Meta:
        model = BiomethaneSupplyPlan
        fields = ["entity_id"]

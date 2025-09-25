from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneSupplyPlan


class BaseBiomethaneSupplyPlanFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact", required=True)


class BiomethaneSupplyPlanFilter(BaseBiomethaneSupplyPlanFilter):
    year = CharFilter(field_name="year", lookup_expr="exact", required=True)

    class Meta:
        model = BiomethaneSupplyPlan
        fields = ["entity_id", "year"]


class BiomethaneSupplyPlanYearsFilter(BaseBiomethaneSupplyPlanFilter):
    class Meta:
        model = BiomethaneSupplyPlan
        fields = ["entity_id"]

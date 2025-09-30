from django_filters import CharFilter, FilterSet

from biomethane.models.biomethane_energy import BiomethaneEnergy


class BiomethaneEnergyFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact")

    class Meta:
        model = BiomethaneEnergy
        fields = ["entity_id"]


class BiomethaneEnergyRetrieveFilter(BiomethaneEnergyFilter):
    year = CharFilter(field_name="year", lookup_expr="exact")

    class Meta:
        model = BiomethaneEnergy
        fields = ["entity_id", "year"]

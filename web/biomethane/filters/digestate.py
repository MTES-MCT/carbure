from django_filters import CharFilter, FilterSet

from biomethane.models import BiomethaneDigestate


class BiomethaneDigestateFilter(FilterSet):
    entity_id = CharFilter(field_name="producer__id", lookup_expr="exact")

    class Meta:
        model = BiomethaneDigestate
        fields = ["entity_id"]


class BiomethaneDigestateRetrieveFilter(BiomethaneDigestateFilter):
    year = CharFilter(field_name="year", lookup_expr="exact")

    class Meta:
        model = BiomethaneDigestate
        fields = ["entity_id", "year"]

from django.utils import timezone
from django_filters import CharFilter, FilterSet, NumberFilter

from tiruert.models import MacFossilFuel


class MacFilter(FilterSet):
    entity_id = CharFilter(field_name="operator_id", lookup_expr="exact", required=True)
    year = NumberFilter(field_name="year", lookup_expr="exact", initial=timezone.now().year, required=True)

    class Meta:
        model = MacFossilFuel
        fields = ["entity_id", "year"]

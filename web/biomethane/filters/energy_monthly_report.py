from django_filters import CharFilter, FilterSet, NumberFilter
from rest_framework.exceptions import PermissionDenied

from biomethane.permissions import is_entity_related_to_biomethane_external_admin


class BiomethaneEnergyMonthlyReportFilter(FilterSet):
    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(method="ignore")  # for typing purposes only

    def filter_by_entity(self, queryset, name, value):
        """
        Filter by entity_id:
        - If producer_id is provided (DREAL/ADEME case), ignore entity_id for the producer filter
        - Otherwise (Producer case), filter by energy__producer_id = entity_id
        """
        if "producer_id" in self.data:
            entity = getattr(self.request, "entity", None)
            if not (entity and is_entity_related_to_biomethane_external_admin(entity)):
                raise PermissionDenied()
            value = self.data["producer_id"]

        return queryset.filter(energy__producer_id=value)

    def ignore(self, queryset, name, value):
        return queryset


class BiomethaneEnergyMonthlyReportYearFilter(BiomethaneEnergyMonthlyReportFilter):
    year = NumberFilter(field_name="energy__year", lookup_expr="exact", required=True)

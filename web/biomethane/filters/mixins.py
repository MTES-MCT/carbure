from django_filters import CharFilter, FilterSet, NumberFilter
from rest_framework.exceptions import PermissionDenied

from biomethane.permissions import is_entity_related_to_biomethane_external_admin


class EntityProducerFilter(FilterSet):
    """
    Generic FilterSet for biomethane models with producer field.
    Can be used directly without subclassing if no additional filters needed.

    Usage in ViewSet:
        filterset_class = EntityProducerFilter
        queryset = BiomethaneEnergy.objects.all()

    Filter logic:
    - Producer: ?entity_id=123 → filters on producer__id=123
    - DREAL: ?entity_id=456&producer_id=789 → filters on producer__id=789
    """

    entity_id = CharFilter(method="filter_by_entity")
    producer_id = CharFilter(method="ignore")  # for typing purposes only

    def filter_by_entity(self, queryset, name, value):
        """
        Filter by entity_id:
        - If producer_id is provided (DREAL case), ignore entity_id for the producer filter
        - Otherwise (Producer case), filter by producer__id = entity_id
        """
        if "producer_id" in self.data:
            entity = getattr(self.request, "entity", None)
            if not (entity and is_entity_related_to_biomethane_external_admin(entity)):
                raise PermissionDenied()
            value = self.data["producer_id"]

        return queryset.filter(producer__id=value)

    def ignore(self, queryset, name, value):
        return queryset


class EntityProducerYearFilter(EntityProducerFilter):
    year = NumberFilter(field_name="year", lookup_expr="exact", required=True)

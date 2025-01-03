from django.db.models import Q
from django_filters import BaseInFilter, CharFilter, DateFilter, FilterSet

from saf.models.constants import SAF_BIOFUEL_TYPES


class OperationFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    date_from = DateFilter(field_name="created_at", lookup_expr="gte")
    date_to = DateFilter(field_name="created_at", lookup_expr="lte")
    type = BaseInFilter(field_name="type", lookup_expr="in")
    status = BaseInFilter(field_name="status", lookup_expr="in")
    customs_category = BaseInFilter(field_name="customs_category", lookup_expr="in")
    biofuel = BaseInFilter(field_name="biofuel__name", lookup_expr="in")
    sector = CharFilter(method="filter_sector")
    from_to = CharFilter(method="filter_from_to")

    def filter_entity(self, queryset, name, value):
        return queryset.filter(Q(credited_entity=value) | Q(debited_entity=value)).distinct()

    def filter_sector(self, queryset, name, value):
        if value == "ESSENCE":
            return queryset.filter(biofuel__compatible_essence=True)
        elif value == "DIESEL":
            return queryset.filter(biofuel__compatible_diesel=True)
        elif value == "SAF":
            return queryset.filter(biofuel__code__in=SAF_BIOFUEL_TYPES)

    def filter_from_to(self, queryset, name, value):
        return queryset.filter(Q(credited_entity__name=value) | Q(debited_entity__name=value)).distinct()

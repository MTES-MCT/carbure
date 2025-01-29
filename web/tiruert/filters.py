from django.db.models import Q
from django_filters import BaseInFilter, CharFilter, DateFilter, FilterSet

from saf.models.constants import SAF_BIOFUEL_TYPES


class OperationFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    date_from = DateFilter(field_name="created_at", lookup_expr="gte")
    date_to = DateFilter(field_name="created_at", lookup_expr="lte")
    operation = BaseInFilter(field_name="type", lookup_expr="in")
    status = BaseInFilter(field_name="status", lookup_expr="in")
    customs_category = BaseInFilter(field_name="customs_category", lookup_expr="in")
    biofuel = BaseInFilter(field_name="biofuel__code", lookup_expr="in")
    sector = CharFilter(method="filter_sector")
    from_to = CharFilter(method="filter_from_to")
    depot = CharFilter(method="filter_depot")
    type = CharFilter(method="filter_type")

    def filter_entity(self, queryset, name, value):
        return queryset.filter(Q(credited_entity=value) | Q(debited_entity=value)).distinct()

    def filter_sector(self, queryset, name, value):
        sectors = self.request.GET.getlist(name)
        if not sectors:
            return queryset

        q_objects = Q()
        if "ESSENCE" in sectors:
            q_objects |= Q(biofuel__compatible_essence=True)
        if "DIESEL" in sectors:
            q_objects |= Q(biofuel__compatible_diesel=True)
        if "SAF" in sectors:
            q_objects |= Q(biofuel__code__in=SAF_BIOFUEL_TYPES)
        return queryset.filter(q_objects).distinct()

    def filter_from_to(self, queryset, name, value):
        return queryset.filter(Q(credited_entity__name=value) | Q(debited_entity__name=value)).distinct()

    def filter_depot(self, queryset, name, value):
        return queryset.filter(Q(from_depot=value) | Q(to_depot=value)).distinct()

    def filter_type(self, queryset, name, value):
        if value == "credit":
            return queryset.filter(type__in=["INCORPORATION", "MAC_BIO", "LIVRAISON_DIRECTE", "ACQUISITION"]).distinct()
        elif value == "debit":
            return queryset.filter(type__in=["CESSION", "TENEUR", "EXPORTATION", "DEVALUATION"]).distinct()
        else:
            return queryset

from django.db.models import Q
from django_filters import BaseInFilter, CharFilter, DateFilter, FilterSet
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ChoiceField, ListField

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
    period = CharFilter(method="filter_period")

    def filter_entity(self, queryset, name, value):
        return queryset.filter(Q(credited_entity=value) | Q(debited_entity=value)).distinct()

    @extend_schema_field(ListField(child=ChoiceField(choices=["ESSENCE", "DIESEL", "SAF"])))
    def filter_sector(self, queryset, name, value):
        sectors = [sector.upper() for sector in self.request.GET.getlist(name)]
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
        entities = self.request.GET.getlist(name)
        return queryset.filter(Q(credited_entity__name__in=entities) | Q(debited_entity__name__in=entities)).distinct()

    @extend_schema_field(ListField(child=CharField()))
    def filter_depot(self, queryset, name, value):
        depots = self.request.GET.getlist(name)
        return queryset.filter(Q(from_depot__name__in=depots) | Q(to_depot__name__in=depots)).distinct()

    @extend_schema_field(ListField(child=ChoiceField(choices=["CREDIT", "DEBIT"])))
    def filter_type(self, queryset, name, value):
        value = value.upper()
        if value == "CREDIT":
            return queryset.filter(type__in=["INCORPORATION", "MAC_BIO", "LIVRAISON_DIRECTE", "ACQUISITION"]).distinct()
        elif value == "DEBIT":
            return queryset.filter(type__in=["CESSION", "TENEUR", "EXPORTATION", "DEVALUATION"]).distinct()
        else:
            return queryset

    @extend_schema_field(ListField(child=CharField()))
    def filter_period(self, queryset, name, value):
        periods = self.request.GET.getlist(name)
        if not periods:
            return queryset

        q_objects = Q()
        for period in periods:
            q_objects |= Q(created_at__year=period[:4], created_at__month=period[4:])
        return queryset.filter(q_objects).distinct()

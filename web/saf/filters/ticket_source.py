from enum import Enum

import django_filters
from django.db.models import Q
from django.db.models.expressions import F
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ChoiceField, ListField

from saf.models import SafTicketSource


class TicketStatusEnum(Enum):
    AVAILABLE = "Available"
    HISTORY = "History"


class TicketSourceFilter(django_filters.FilterSet):
    entity_id = django_filters.NumberFilter(field_name="added_by_id", required=True)
    year = django_filters.NumberFilter(field_name="year")
    periods = django_filters.BaseInFilter(field_name="delivery_period", lookup_expr="in")
    feedstocks = django_filters.BaseInFilter(field_name="feedstock__code", lookup_expr="in")
    clients = django_filters.BaseInFilter(field_name="saf_tickets__client__name", lookup_expr="in")

    countries_of_origin = django_filters.BaseInFilter(field_name="country_of_origin__code_pays", lookup_expr="in")
    production_sites = django_filters.BaseInFilter(field_name="carbure_production_site__name", lookup_expr="in")
    delivery_sites = django_filters.BaseInFilter(field_name="parent_lot__carbure_delivery_site__name", lookup_expr="in")
    status = django_filters.ChoiceFilter(
        choices=[(item.name, item.value) for item in TicketStatusEnum],
        method="filter_status",
    )
    suppliers = django_filters.BaseInFilter(method="filter_suppliers")

    order = django_filters.OrderingFilter(
        fields=(
            ("total_volume", "volume"),
            ("delivery_period", "period"),
            ("feedstock__code", "feedstock"),
            ("ghg_reduction", "ghg_reduction"),
        )
    )

    class Meta:
        model = SafTicketSource
        fields = [
            "entity_id",
            "year",
            "periods",
            "feedstocks",
            "clients",
            "suppliers",
            "countries_of_origin",
            "production_sites",
            "delivery_sites",
            "status",
        ]

    @extend_schema_field(ChoiceField(choices=["HISTORY", "AVAILABLE"]))
    def filter_status(self, queryset, name, value):
        if value == "AVAILABLE":
            return queryset.filter(assigned_volume__lt=F("total_volume"))
        elif value == "HISTORY":
            return queryset.filter(assigned_volume__gte=F("total_volume"))
        else:
            raise Exception(f"Status '{value}' does not exist for ticket sources")

    @extend_schema_field(ListField(child=CharField(), help_text="Comma-separated list of supplier names"))
    def filter_suppliers(self, queryset, name, value):
        suppliers = self.request.GET.getlist(name)
        if not suppliers:
            return queryset

        return queryset.filter(
            Q(parent_lot__carbure_supplier__name__in=suppliers)
            | Q(parent_lot__unknown_supplier__in=suppliers)
            | Q(parent_ticket__supplier__name__in=suppliers)
        )

from enum import Enum

import django_filters
from django.db.models import F, Q
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ChoiceField, ListField

from saf.models import SafTicketSource


class TicketStatusEnum(Enum):
    AVAILABLE = "Available"
    HISTORY = "History"


class TicketSourceFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="year")

    period = django_filters.AllValuesMultipleFilter(field_name="delivery_period")
    feedstock = django_filters.AllValuesMultipleFilter(field_name="feedstock__code")
    added_by = django_filters.AllValuesMultipleFilter(field_name="added_by__name")
    clients = django_filters.AllValuesMultipleFilter(field_name="saf_tickets__client__name")
    supplier = django_filters.CharFilter(method="filter_supplier")
    country_of_origin = django_filters.AllValuesMultipleFilter(field_name="country_of_origin__code_pays")
    production_site = django_filters.AllValuesMultipleFilter(field_name="carbure_production_site__name")
    delivery_site = django_filters.AllValuesMultipleFilter(field_name="parent_lot__carbure_delivery_site__name")

    status = django_filters.ChoiceFilter(
        choices=[(item.name, item.value) for item in TicketStatusEnum],
        method="filter_status",
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ("total_volume", "volume"),
            ("delivery_period", "period"),
            ("feedstock__code", "feedstock"),
            ("ghg_reduction", "ghg_reduction"),
            ("added_by__name", "added_by"),
        )
    )

    @extend_schema_field(ChoiceField(choices=["HISTORY", "AVAILABLE"]))
    def filter_status(self, queryset, name, value):
        if value == "AVAILABLE":
            return queryset.filter(assigned_volume__lt=F("total_volume"))
        elif value == "HISTORY":
            return queryset.filter(assigned_volume__gte=F("total_volume"))
        else:
            raise Exception(f"Status '{value}' does not exist for ticket sources")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of suppliers provided via ?suppliers=supplier1&suppliers=supplier2&suppliers=supplier3",
            required=False,
        )
    )
    def filter_supplier(self, queryset, name, value):
        request = self.request
        suppliers_list = request.GET.getlist("supplier")
        return queryset.filter(
            Q(parent_lot__carbure_supplier__name__in=suppliers_list)
            | Q(parent_lot__unknown_supplier__in=suppliers_list)
            | Q(parent_ticket__supplier__name__in=suppliers_list)
        )

    class Meta:
        model = SafTicketSource
        fields = [
            "year",
            "period",
            "feedstock",
            "clients",
            "supplier",
            "country_of_origin",
            "production_site",
            "delivery_site",
            "status",
            "added_by",
        ]

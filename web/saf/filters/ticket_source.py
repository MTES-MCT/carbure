from enum import Enum

import django_filters
from django.db.models import Q
from django.db.models.expressions import F
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ChoiceField, IntegerField, ListField

from saf.models import SafTicketSource


class TicketStatusEnum(Enum):
    AVAILABLE = "Available"
    HISTORY = "History"


class TicketSourceFilter(django_filters.FilterSet):
    entity_id = django_filters.NumberFilter(field_name="added_by_id", required=True)
    year = django_filters.NumberFilter(field_name="year")

    periods = django_filters.CharFilter(method="filter_periods")
    feedstocks = django_filters.CharFilter(method="filter_feedstocks")
    clients = django_filters.CharFilter(field_name="saf_tickets__client__name", method="filter_clients")
    countries_of_origin = django_filters.CharFilter(method="filter_countries_of_origin")
    production_sites = django_filters.CharFilter(method="filter_production_sites")
    delivery_sites = django_filters.CharFilter(method="filter_delivery_sites")

    status = django_filters.ChoiceFilter(
        choices=[(item.name, item.value) for item in TicketStatusEnum],
        method="filter_status",
    )
    suppliers = django_filters.CharFilter(method="filter_suppliers")

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

    def filter_multiple_values(self, queryset, field_name, param_name):
        values = self.data.getlist(param_name)
        if values:
            return queryset.filter(Q(**{f"{field_name}__in": values}))
        return queryset

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
    def filter_suppliers(self, queryset, name, value):
        request = self.request
        suppliers_list = request.GET.getlist("suppliers")
        return queryset.filter(
            Q(parent_lot__carbure_supplier__name__in=suppliers_list)
            | Q(parent_lot__unknown_supplier__in=suppliers_list)
            | Q(parent_ticket__supplier__name__in=suppliers_list)
        )

    @extend_schema_field(
        ListField(
            child=IntegerField(),
            help_text="List of periods provided via ?periods=period1&periods=period2&periods=period3",
            required=False,
        )
    )
    def filter_periods(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "delivery_period", "periods")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of feedstocks provided via ?feedstocks=feedstock1&feedstocks=feedstock2",
            required=False,
        )
    )
    def filter_feedstocks(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "feedstock__code", "feedstocks")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of clients provided via ?clients=client1&clients=client2&clients=client3",
            required=False,
        )
    )
    def filter_clients(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "saf_tickets__client__name", "clients")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of countries of origin provided via ?countries_of_origin=country1&countries_of_origin=country2",
            required=False,
        )
    )
    def filter_countries_of_origin(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "country_of_origin__code_pays", "countries_of_origin")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of production sites provided via ?production_sites=site1&production_sites=site2",
            required=False,
        )
    )
    def filter_production_sites(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "carbure_production_site__name", "production_sites")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of delivery sites provided via ?delivery_sites=site1&delivery_sites=site2",
            required=False,
        )
    )
    def filter_delivery_sites(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "parent_lot__carbure_delivery_site__name", "delivery_sites")

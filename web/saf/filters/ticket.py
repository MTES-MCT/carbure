import django_filters
from django.db.models import Q
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, IntegerField, ListField

from core.models import Entity
from saf.models import SafTicket


class TicketFilter(django_filters.FilterSet):
    entity_id = django_filters.NumberFilter(field_name="entity_id", method="filter_entity_id", required=True)
    status = django_filters.ChoiceFilter(choices=SafTicket.ticket_statuses)
    year = django_filters.NumberFilter(field_name="year")

    periods = django_filters.CharFilter(method="filter_periods")
    feedstocks = django_filters.CharFilter(method="filter_feedstocks")
    clients = django_filters.CharFilter(method="filter_clients")
    suppliers = django_filters.CharFilter(method="filter_suppliers")
    countries_of_origin = django_filters.CharFilter(method="filter_countries_of_origin")
    production_sites = django_filters.CharFilter(method="filter_production_sites")

    order = django_filters.OrderingFilter(
        fields=(
            ("client__name", "client"),
            ("volume", "volume"),
            ("assignment_period", "period"),
            ("feedstock__code", "feedstock"),
            ("ghg_reduction", "ghg_reduction"),
            ("created_at", "created_at"),
            ("suppliers", "suppliers"),
        )
    )

    class Meta:
        model = SafTicket
        fields = [
            "entity_id",
            "status",
            "year",
            "periods",
            "feedstocks",
            "clients",
            "suppliers",
            "countries_of_origin",
            "production_sites",
        ]

    def filter_multiple_values(self, queryset, field_name, param_name):
        values = self.data.getlist(param_name)
        if values:
            return queryset.filter(Q(**{f"{field_name}__in": values}))
        return queryset

    def filter_entity_id(self, queryset, name, value):
        ticket_type = self.data.get("type")
        entity = Entity.objects.get(id=value)
        if entity.entity_type == Entity.AIRLINE:
            return queryset.filter(client_id=value)

        if ticket_type == "assigned":
            return queryset.filter(supplier_id=value)
        elif ticket_type == "received":
            return queryset.filter(client_id=value)
        return queryset

    @extend_schema_field(
        ListField(
            child=IntegerField(),
            help_text="List of periods provided via ?periods=period1&periods=period2&periods=period3",
            required=False,
        )
    )
    def filter_periods(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "assignment_period", "periods")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of feedstocks provided via ?feedstocks=feedstock1&feedstocks=feedstock2&feedstocks=feedstock3",
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
        return self.filter_multiple_values(queryset, "client__name", "clients")

    @extend_schema_field(
        ListField(
            child=CharField(),
            help_text="List of suppliers provided via ?suppliers=supplier1&suppliers=supplier2&suppliers=supplier3",
            required=False,
        )
    )
    def filter_suppliers(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "supplier__name", "suppliers")

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

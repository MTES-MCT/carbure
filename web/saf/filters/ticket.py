import django_filters

from core.models import Entity
from saf.models import SafTicket


class TicketFilter(django_filters.FilterSet):
    entity_id = django_filters.NumberFilter(field_name="entity_id", method="filter_entity_id", required=True)
    status = django_filters.ChoiceFilter(choices=SafTicket.ticket_statuses)
    year = django_filters.NumberFilter(field_name="year")
    periods = django_filters.BaseInFilter(field_name="assignment_period", lookup_expr="in")
    feedstocks = django_filters.BaseInFilter(field_name="feedstock__code", lookup_expr="in")
    clients = django_filters.BaseInFilter(field_name="client__name", lookup_expr="in")
    suppliers = django_filters.BaseInFilter(field_name="supplier__name", lookup_expr="in")
    countries_of_origin = django_filters.BaseInFilter(field_name="country_of_origin__code_pays", lookup_expr="in")
    production_sites = django_filters.BaseInFilter(field_name="carbure_production_site__name", lookup_expr="in")
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

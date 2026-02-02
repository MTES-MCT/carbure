import django_filters

from core.models import Entity
from saf.models import SafTicket


class TicketFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=SafTicket.ticket_statuses)
    year = django_filters.NumberFilter(field_name="year")

    supplier = django_filters.AllValuesMultipleFilter(field_name="supplier__name")
    client = django_filters.AllValuesMultipleFilter(field_name="client__name")
    client_type = django_filters.AllValuesMultipleFilter(field_name="client__entity_type")
    period = django_filters.AllValuesMultipleFilter(field_name="assignment_period")
    feedstock = django_filters.AllValuesMultipleFilter(field_name="feedstock__code")
    country_of_origin = django_filters.AllValuesMultipleFilter(field_name="country_of_origin__code_pays")
    production_site = django_filters.AllValuesMultipleFilter(field_name="carbure_production_site__name")
    consumption_type = django_filters.MultipleChoiceFilter(
        field_name="consumption_type", choices=SafTicket.CONSUMPTION_TYPES
    )
    reception_airport = django_filters.AllValuesMultipleFilter(field_name="reception_airport__name")
    origin_depot = django_filters.AllValuesMultipleFilter(field_name="origin_lot_site__name")

    order_by = django_filters.OrderingFilter(
        fields=(
            ("client__name", "client"),
            ("volume", "volume"),
            ("assignment_period", "period"),
            ("feedstock__code", "feedstock"),
            ("ghg_reduction", "ghg_reduction"),
            ("created_at", "created_at"),
            ("supplier__name", "supplier"),
            ("consumption_type", "consumption_type"),
            ("reception_airport__name", "reception_airport"),
        )
    )

    def filter_type(self, queryset, name, value):
        entity = Entity.objects.get(pk=value)
        ticket_type = self.data.get("type")
        if entity.entity_type in (Entity.AIRLINE, Entity.OPERATOR, Entity.SAF_TRADER):
            if ticket_type == "assigned":
                return queryset.filter(supplier=entity)
            elif ticket_type == "received":
                return queryset.filter(client=entity)
        return queryset

    class Meta:
        model = SafTicket
        fields = [
            "status",
            "year",
            "supplier",
            "client",
            "client_type",
            "period",
            "feedstock",
            "country_of_origin",
            "production_site",
            "consumption_type",
            "reception_airport",
            "origin_depot",
        ]

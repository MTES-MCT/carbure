import django_filters

from core.models import Entity
from saf.models import SafTicket


class TicketFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=SafTicket.ticket_statuses)
    entity_id = django_filters.NumberFilter(field_name="entity_id", method="filter_type", required=True)
    year = django_filters.NumberFilter(field_name="year")

    period = django_filters.BaseInFilter(field_name="assignment_period", lookup_expr="in")
    biofuel = django_filters.BaseInFilter(field_name="biofuel__code", lookup_expr="in")
    feedstock = django_filters.BaseInFilter(field_name="feedstock__code", lookup_expr="in")
    client = django_filters.BaseInFilter(field_name="client__name", lookup_expr="in")
    supplier = django_filters.BaseInFilter(field_name="supplier__name", lookup_expr="in")
    country_of_origin = django_filters.BaseInFilter(field_name="country_of_origin__code_pays", lookup_expr="in")
    production_site = django_filters.BaseInFilter(field_name="carbure_production_site__name", lookup_expr="in")
    consumption_type = django_filters.BaseInFilter(field_name="consumption_type", lookup_expr="in")

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
            "entity_id",
            "status",
            "year",
            "period",
            "feedstock",
            "client",
            "supplier",
            "country_of_origin",
            "production_site",
            "consumption_type",
        ]

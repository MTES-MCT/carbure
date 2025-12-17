from enum import Enum

import django_filters
from django.db.models import F
from django.db.models.functions import Coalesce
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import ChoiceField

from core.filters import AllAnnotatedValuesMultipleFilter
from saf.models import SafTicketSource


class TicketStatusEnum(Enum):
    AVAILABLE = "Available"
    HISTORY = "History"


class TicketSourceFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=[(item.name, item.value) for item in TicketStatusEnum],
        method="filter_status",
    )

    year = django_filters.NumberFilter(field_name="year")
    added_by = django_filters.AllValuesMultipleFilter(field_name="added_by__name")

    supplier = extend_schema_field(OpenApiTypes.STR)(
        AllAnnotatedValuesMultipleFilter(
            field_name="supplier",
            annotation=Coalesce(
                "parent_lot__carbure_supplier__name",
                "parent_lot__unknown_supplier",
                "parent_ticket__supplier__name",
            ),
        )
    )

    client = django_filters.AllValuesMultipleFilter(field_name="saf_tickets__client__name")
    period = django_filters.AllValuesMultipleFilter(field_name="delivery_period")
    feedstock = django_filters.AllValuesMultipleFilter(field_name="feedstock__code")
    country_of_origin = django_filters.AllValuesMultipleFilter(field_name="country_of_origin__code_pays")
    production_site = django_filters.AllValuesMultipleFilter(field_name="carbure_production_site__name")
    origin_depot = django_filters.AllValuesMultipleFilter(field_name="origin_lot_site__name")

    order_by = django_filters.OrderingFilter(
        fields=(
            ("total_volume", "volume"),
            ("delivery_period", "delivery"),
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

    class Meta:
        model = SafTicketSource
        fields = [
            "status",
            "year",
            "added_by",
            "supplier",
            "client",
            "period",
            "feedstock",
            "country_of_origin",
            "production_site",
            "origin_depot",
        ]

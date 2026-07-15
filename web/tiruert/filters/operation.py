from datetime import datetime  # noqa: I001
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models import IntegerField, Q
from django.db.models.functions import Cast, Coalesce, Substr
from django_filters import (
    CharFilter,
    FilterSet,
    NumberFilter,
    AllValuesMultipleFilter,
    MultipleChoiceFilter,
)
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import (
    CharField,
    IntegerField as SerializerIntegerField,
    ListField,
)

from core.filters import AllAnnotatedValuesMultipleFilter
from core.models import Entity, ExternalAdminRights, MatierePremiere
from .custom_filters import CustomOrderingFilter
from tiruert.models.operation import Operation


class BaseFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    selected_entity_id = NumberFilter(method="ignore")
    operation = MultipleChoiceFilter(
        choices=Operation.OPERATION_TYPES + (("ACQUISITION", "ACQUISITION"),), field_name="type"
    )
    biofuel = AllValuesMultipleFilter(field_name="biofuel__code")
    sector = MultipleChoiceFilter(choices=Operation.SECTOR_CODE_CHOICES, field_name="_sector")
    from_to = CharFilter(method="filter_from_to")
    depot = CharFilter(method="filter_depot")
    type = MultipleChoiceFilter(choices=(("CREDIT", "CREDIT"), ("DEBIT", "DEBIT")), field_name="_transaction")
    period = CharFilter(method="filter_period")
    customs_category = MultipleChoiceFilter(choices=MatierePremiere.MP_CATEGORIES)
    status = MultipleChoiceFilter(choices=Operation.OPERATION_STATUSES)
    feedstock = AllValuesMultipleFilter(field_name="details__lot__feedstock__code")
    origin_country = AllValuesMultipleFilter(field_name="details__lot__country_of_origin__code_pays")
    durability_period = AllValuesMultipleFilter(field_name="durability_period")

    order_by = CustomOrderingFilter(
        fields=(
            ("status", "status"),
            ("created_at", "created_at"),
            ("_sector", "sector"),
            ("biofuel__code", "biofuel"),
            ("customs_category", "customs_category"),
            ("_type", "type"),
            ("_depot", "depot"),
            ("_entity", "from_to"),
            ("_quantity", "quantity"),
            ("durability_period", "durability_period"),
        ),
        extra_valid_fields=[
            "available_balance",
            "pending_operations",
            "saved_emissions",
        ],
    )

    def filter_entity(self, queryset, name, value):
        entity = getattr(self.request, "entity", None)

        # DGEC / DGDDI case: ignore entity_id for filtering, entity_id is just for permissions
        if "selected_entity_id" in self.data:
            if not entity.entity_type == Entity.ADMIN and not entity.has_external_admin_right(
                ExternalAdminRights.DGDDI_NATIONAL
            ):
                raise PermissionDenied()
            value = self.data["selected_entity_id"]

        # For DGDDI external admins, filter by accessible depots
        if entity.has_external_admin_right(ExternalAdminRights.DGDDI):
            accessible_depot_ids = entity.get_accessible_depots().values_list("id", flat=True)
            depot_filter = Q(to_depot_id__in=accessible_depot_ids)
            return queryset.filter(depot_filter)

        return queryset.filter(Q(credited_entity=value) | Q(debited_entity=value)).distinct()

    def filter_from_to(self, queryset, name, value):
        entities = self.request.GET.getlist(name)
        return queryset.filter(Q(credited_entity__name__in=entities) | Q(debited_entity__name__in=entities)).distinct()

    @extend_schema_field(ListField(child=CharField()))
    def filter_depot(self, queryset, name, value):
        depots = self.request.GET.getlist(name)
        return queryset.filter(Q(from_depot__name__in=depots) | Q(to_depot__name__in=depots)).distinct()

    @extend_schema_field(ListField(child=CharField()))
    def filter_period(self, queryset, name, value):
        periods = self.request.GET.getlist(name)
        if not periods:
            return queryset

        # Use the timezone from settings
        django_timezone = ZoneInfo(settings.TIME_ZONE)

        q_objects = Q()

        for period in periods:
            # We have to do all this stuff because scalingo doesn't support mysql timezone
            year = int(period[:4])
            month = int(period[4:])

            # Calculate the next month and year
            if month == 12:
                next_year = year + 1
                next_month = 1
            else:
                next_year = year
                next_month = month + 1

            # Dates in UTC
            start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=django_timezone).astimezone(ZoneInfo("UTC"))
            end_date = datetime(next_year, next_month, 1, 0, 0, 0, tzinfo=django_timezone).astimezone(ZoneInfo("UTC"))

            q_objects |= Q(created_at__gte=start_date, created_at__lt=end_date)

        return queryset.filter(q_objects).distinct()

    def ignore(self, queryset, name, value):
        return queryset


class OperationFilter(BaseFilter):
    years = extend_schema_field(SerializerIntegerField())(
        AllAnnotatedValuesMultipleFilter(
            field_name="year",
            annotation=Coalesce(
                "declaration_year",
                Cast(
                    Substr("durability_period", 1, 4),
                    output_field=IntegerField(),
                ),
                output_field=IntegerField(),
            ),
        )
    )
    pass


class OperationFilterForBalance(BaseFilter):
    # Lot-level filters are handled by Prefetch in BalanceService, not at the Operation queryset level
    ges_bound_min = NumberFilter(method="ignore")
    ges_bound_max = NumberFilter(method="ignore")
    feedstock = AllValuesMultipleFilter(field_name="details__lot__feedstock__code", method="ignore")
    origin_country = AllValuesMultipleFilter(field_name="details__lot__country_of_origin__code_pays", method="ignore")
    # durability_period is resolved to specific lot_ids in the view and passed via detail_filters
    durability_period = AllValuesMultipleFilter(method="ignore")

    def ignore(self, queryset, name, value):
        return queryset

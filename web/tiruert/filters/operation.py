from django.db.models import IntegerField, Q
from django.db.models.functions import Cast, Coalesce, Substr
from django_filters import (
    CharFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
)
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import CharField, ListField

from core.filters import MultiValueInFilter
from core.models import Entity, ExternalAdminRights, MatierePremiere
from core.utils import get_month_bounds_utc
from tiruert.models.operation import Operation

from .custom_filters import CustomOrderingFilter


class BaseFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    selected_entity_id = NumberFilter(method="ignore")
    operation = MultipleChoiceFilter(
        choices=Operation.OPERATION_TYPES + (("ACQUISITION", "ACQUISITION"),), field_name="type"
    )
    biofuel = MultiValueInFilter(field_name="biofuel__code")
    sector = MultipleChoiceFilter(choices=Operation.SECTOR_CODE_CHOICES, field_name="_sector")
    from_to = CharFilter(method="filter_from_to")
    depot = CharFilter(method="filter_depot")
    type = MultipleChoiceFilter(choices=(("CREDIT", "CREDIT"), ("DEBIT", "DEBIT")), field_name="_transaction")
    period = CharFilter(method="filter_period")
    customs_category = MultipleChoiceFilter(choices=MatierePremiere.MP_CATEGORIES)
    status = MultipleChoiceFilter(choices=Operation.OPERATION_STATUSES)
    feedstock = MultiValueInFilter(field_name="details__lot__feedstock__code", distinct=True)
    origin_country = MultiValueInFilter(field_name="details__lot__country_of_origin__code_pays", distinct=True)
    durability_period = MultiValueInFilter(field_name="durability_period")

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

        q_objects = Q()

        for period in periods:
            start, end = get_month_bounds_utc(period)
            q_objects |= Q(created_at__gte=start, created_at__lt=end)

        return queryset.filter(q_objects).distinct()

    def ignore(self, queryset, name, value):
        return queryset


class OperationFilter(BaseFilter):
    years = CharFilter(method="filter_years")

    @extend_schema_field(ListField(child=CharField()))
    def filter_years(self, queryset, name, value):
        years = self.request.GET.getlist(name)
        if not years:
            return queryset

        return queryset.annotate(
            year=Coalesce(
                "declaration_year",
                Cast(
                    Substr("durability_period", 1, 4),
                    output_field=IntegerField(),
                ),
            )
        ).filter(year__in=years)


class OperationFilterForBalance(BaseFilter):
    # Lot-level filters are handled by Prefetch in BalanceService, not at the Operation queryset level
    ges_bound_min = NumberFilter(method="ignore")
    ges_bound_max = NumberFilter(method="ignore")
    feedstock = MultiValueInFilter(method="ignore")
    origin_country = MultiValueInFilter(method="ignore")
    # durability_period is resolved to specific lot_ids in the view and passed via detail_filters
    durability_period = MultiValueInFilter(method="ignore")

    def ignore(self, queryset, name, value):
        return queryset

from datetime import datetime  # noqa: I001
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db.models import Q
from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter, AllValuesMultipleFilter, MultipleChoiceFilter
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import CharField, ListField

from .custom_filters import CustomOrderingFilter
from tiruert.models.operation import Operation


class BaseFilter(FilterSet):
    entity_id = CharFilter(method="filter_entity")
    date_to = DateFilter(field_name="created_at", lookup_expr="lte")
    operation = MultipleChoiceFilter(
        choices=Operation.OPERATION_TYPES + (("ACQUISITION", "ACQUISITION"),), field_name="type"
    )
    biofuel = AllValuesMultipleFilter(field_name="biofuel__code")
    sector = MultipleChoiceFilter(choices=Operation.SECTOR_CODE_CHOICES, field_name="_sector")
    from_to = CharFilter(method="filter_from_to")
    depot = CharFilter(method="filter_depot")
    type = MultipleChoiceFilter(choices=(("CREDIT", "CREDIT"), ("DEBIT", "DEBIT")), field_name="_transaction")
    period = CharFilter(method="filter_period")

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
        ),
        extra_valid_fields=[
            "available_balance",
            "pending_operations",
            "saved_emissions",
        ],
    )

    def filter_entity(self, queryset, name, value):
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

    class Meta:
        model = Operation
        fields = [
            "biofuel",
            "customs_category",
            "sector",
            "from_to",
            "depot",
            "type",
            "operation",
            "status",
            "entity_id",
            "date_to",
            "period",
        ]


class OperationFilter(BaseFilter):
    date_from = DateFilter(field_name="created_at", lookup_expr="gte")


class OperationFilterForBalance(BaseFilter):
    ges_bound_min = NumberFilter(method="ignore")
    ges_bound_max = NumberFilter(method="ignore")

    def ignore(self, queryset, name, value):
        return queryset

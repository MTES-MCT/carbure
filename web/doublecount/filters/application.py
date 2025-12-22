import django_filters

from doublecount.models import DoubleCountingApplication


class ApplicationFilter(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=(
            ("production_site__name", "production_site"),
            ("period_start", "valid_until"),
            ("production_site__created_by__name", "producer"),
            ("created_at", "created_at"),
            ("certificate_id", "certificate_id"),
        )
    )
    certificate_id = django_filters.CharFilter(field_name="certificate_id", lookup_expr="exact")
    producers = django_filters.CharFilter(field_name="production_site__created_by__name", lookup_expr="exact")
    production_sites = django_filters.CharFilter(field_name="production_site__name", lookup_expr="exact")
    status = django_filters.CharFilter(method="filter_status")

    # Additional filter without method for FiltersActionFactory
    # allows retrieving the list of available statuses
    status_values = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = DoubleCountingApplication
        fields = ["order_by", "certificate_id", "producers", "production_sites", "status_values"]

    def filter_status(self, queryset, name, value):
        if value == "rejected":
            return queryset.filter(status=DoubleCountingApplication.REJECTED)
        elif value == "pending":
            return queryset.exclude(
                status__in=[
                    DoubleCountingApplication.ACCEPTED,
                    DoubleCountingApplication.REJECTED,
                ]
            )
        else:
            return queryset

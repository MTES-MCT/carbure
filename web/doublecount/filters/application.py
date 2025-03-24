import django_filters
from django.db.models import Q

from doublecount.models import DoubleCountingApplication


class ApplicationFilter(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=(
            ("production_site__name", "production_site"),
            ("valid_until", "valid_until"),
        )
    )
    certificate_id = django_filters.CharFilter(method="filter_certificate_id")
    producers = django_filters.CharFilter(method="filter_producers")
    production_sites = django_filters.CharFilter(method="filter_production_sites")

    class Meta:
        model = DoubleCountingApplication
        fields = ["order_by"]

    def filter_multiple_values(self, queryset, field_name, param_name):
        values = self.data.getlist(param_name)
        if values:
            return queryset.filter(Q(**{f"{field_name}__in": values}))
        return queryset

    def filter_certificate_id(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "certificate_id", "certificate_id")

    def filter_producers(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "production_site__created_by__name", "producers")

    def filter_production_sites(self, queryset, name, value):
        return self.filter_multiple_values(queryset, "production_site__name", "production_sites")

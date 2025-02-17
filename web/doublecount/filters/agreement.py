import django_filters

from certificates.models import DoubleCountingRegistration


class AgreementFilter(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=(
            ("production_site__name", "production_site"),
            ("valid_until", "valid_until"),
        )
    )
    certificate_id = django_filters.BaseInFilter(field_name="certificate_id", lookup_expr="in")
    producers = django_filters.BaseInFilter(field_name="production_site__created_by__name", lookup_expr="in")
    production_sites = django_filters.BaseInFilter(field_name="production_site__name", lookup_expr="in")

    class Meta:
        model = DoubleCountingRegistration
        fields = ["order_by"]

import django_filters

from certificates.models import DoubleCountingRegistration


class AgreementFilter(django_filters.FilterSet):
    order_by = django_filters.OrderingFilter(
        fields=(
            ("production_site__name", "production_site"),
            ("valid_until", "valid_until"),
        )
    )

    class Meta:
        model = DoubleCountingRegistration
        fields = ["order_by"]

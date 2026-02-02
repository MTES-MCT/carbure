import django_filters

from core.filters import MultipleBooleanFilter
from elec.models import ElecTransferCertificate


class TransferCertificateFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    year = django_filters.NumberFilter(field_name="transfer_date__year")
    month = django_filters.MultipleChoiceFilter(
        field_name="transfer_date__month",
        choices=[(i, i) for i in range(1, 13)],
    )
    cpo = django_filters.AllValuesMultipleFilter(field_name="supplier__name")
    operator = django_filters.AllValuesMultipleFilter(field_name="client__name")
    used_in_tiruert = MultipleBooleanFilter(field_name="used_in_tiruert")

    order_by = django_filters.OrderingFilter(
        fields=(
            ("status", "status"),
            ("energy_amount", "energy_amount"),
            ("supplier__name", "cpo"),
            ("client__name", "operator"),
            ("certificate_id", "certificate_id"),
            ("transfer_date", "transfer_date"),
            ("consumption_date", "consumption_date"),
        )
    )

    class Meta:
        model = ElecTransferCertificate
        fields = [
            "status",
            "year",
            "month",
            "cpo",
            "operator",
            "used_in_tiruert",
        ]

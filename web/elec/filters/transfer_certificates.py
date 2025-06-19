import django_filters

from elec.models import ElecTransferCertificate


class TransferCertificateFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="transfer_date__year")
    month = django_filters.NumberFilter(field_name="transfer_date__month")
    status = django_filters.CharFilter(field_name="status")
    cpo = django_filters.BaseInFilter(field_name="supplier__name", lookup_expr="in")
    operator = django_filters.BaseInFilter(field_name="client__name", lookup_expr="in")
    used_in_tiruert = django_filters.BooleanFilter(field_name="used_in_tiruert")

    order_by = django_filters.OrderingFilter(
        fields=(
            ("status", "status"),
            ("energy_amount", "energy_amount"),
            ("supplier__name", "cpo"),
            ("client__name", "operator"),
            ("certificate_id", "certificate_id"),
            ("transfer_date", "transfer_date"),
            ("transfer_date", "transfer_date"),
            ("consumption_date", "consumption_date"),
        )
    )

    class Meta:
        model = ElecTransferCertificate
        fields = [
            "certificate_id",
            "status",
            "supplier",
            "client",
            "transfer_date",
            "consumption_date",
            "energy_amount",
            "used_in_tiruert",
        ]

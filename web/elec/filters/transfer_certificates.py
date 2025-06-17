import django_filters

from elec.models import ElecTransferCertificate


class TransferCertificateFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="transfer_date__year")
    status = django_filters.BaseInFilter(field_name="status", lookup_expr="in")
    cpo = django_filters.BaseInFilter(field_name="supplier__name", lookup_expr="in")
    operator = django_filters.BaseInFilter(field_name="client__name", lookup_expr="in")

    order_by = django_filters.OrderingFilter(
        fields=(
            ("status", "status"),
            ("energy_amount", "energy_amount"),
            ("supplier__name", "cpo"),
            ("client__name", "operator"),
            ("certificate_id", "certificate_id"),
            ("transfer_date", "transfer_date"),
            ("accepted_date", "accepted_date"),
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
            "accepted_date",
            "energy_amount",
        ]

import django_filters

from elec.models.elec_transfer_certificate import ElecTransferCertificate


class TransfertCertificateFilter(django_filters.FilterSet):
    entity_id = django_filters.NumberFilter(
        field_name="entity_id",
        method="filter_entity_id",
        label="Entity Id",
        required=True,
    )
    year = django_filters.NumberFilter(field_name="transfer_date__year", label="Transfer date year")
    status = django_filters.ChoiceFilter(choices=ElecTransferCertificate.STATUS)
    transfer_date = django_filters.BaseInFilter(field_name="transfer_date", lookup_expr="in")
    cpo = django_filters.BaseInFilter(field_name="supplier__name", lookup_expr="in")
    operator = django_filters.BaseInFilter(field_name="client__name", lookup_expr="in")

    order = django_filters.OrderingFilter(
        fields=(
            ("transfer_date", "transfer_date"),
            ("energy_amount", "energy_amount"),
            ("supplier__name", "cpo"),
            ("client__name", "operator"),
        )
    )

    class Meta:
        model = ElecTransferCertificate
        fields = [
            "entity_id",
            "status",
            "year",
            "transfer_date",
            "cpo",
            "operator",
        ]

    def filter_entity_id(self, queryset, name, value):
        return queryset.filter(client_id=value)

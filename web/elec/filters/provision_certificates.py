import django_filters

from elec.models import ElecProvisionCertificate


class ProvisionCertificateFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="year")
    quarter = django_filters.BaseInFilter(field_name="quarter", lookup_expr="in")
    operating_unit = django_filters.BaseInFilter(field_name="operating_unit", lookup_expr="in")
    cpo = django_filters.BaseInFilter(field_name="cpo__name", lookup_expr="in")

    order = django_filters.OrderingFilter(
        fields=(
            ("quarter", "quarter"),
            ("energy_amount", "energy_amount"),
            ("cpo__name", "cpo"),
            ("operating_unit", "operating_unit"),
            ("source", "source"),
        )
    )

    class Meta:
        model = ElecProvisionCertificate
        fields = [
            "cpo",
            "quarter",
            "year",
            "operating_unit",
            "source",
            "energy_amount",
        ]

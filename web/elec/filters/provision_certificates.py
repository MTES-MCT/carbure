import django_filters

from elec.models import ElecProvisionCertificate


class ProvisionCertificateFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="year")
    quarter = django_filters.AllValuesMultipleFilter(field_name="quarter")
    operating_unit = django_filters.AllValuesMultipleFilter(field_name="operating_unit")
    cpo = django_filters.AllValuesMultipleFilter(field_name="cpo__name")
    source = django_filters.AllValuesMultipleFilter(field_name="source")

    order_by = django_filters.OrderingFilter(
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
            "year",
            "quarter",
            "operating_unit",
            "cpo",
            "source",
        ]

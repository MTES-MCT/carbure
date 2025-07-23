import django_filters

from elec.models import ElecProvisionCertificate


class ProvisionCertificateFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(method="filter_status")
    year = django_filters.NumberFilter(field_name="year")
    quarter = django_filters.BaseInFilter(field_name="quarter", lookup_expr="in")
    operating_unit = django_filters.BaseInFilter(field_name="operating_unit", lookup_expr="in")
    cpo = django_filters.BaseInFilter(field_name="cpo__name", lookup_expr="in")
    source = django_filters.BaseInFilter(field_name="source", lookup_expr="in")

    order_by = django_filters.OrderingFilter(
        fields=(
            ("quarter", "quarter"),
            ("remaining_energy_amount", "remaining_energy_amount"),
            ("cpo__name", "cpo"),
            ("operating_unit", "operating_unit"),
            ("source", "source"),
        )
    )

    def filter_status(self, queryset, name, value):
        if value == "available":
            return queryset.filter(remaining_energy_amount__gt=0.01)
        elif value == "history":
            return queryset.filter(remaining_energy_amount__lte=0.01)

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

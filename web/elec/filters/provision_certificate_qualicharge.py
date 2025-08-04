from django_filters import BaseInFilter, BooleanFilter, FilterSet, MultipleChoiceFilter

from elec.models import ElecProvisionCertificateQualicharge


class ProvisionCertificateQualichargeFilter(FilterSet):
    cpo = BaseInFilter(field_name="cpo__name", lookup_expr="in")
    not_validated = BooleanFilter(method="filter_not_validated")
    validated_by = MultipleChoiceFilter(choices=ElecProvisionCertificateQualicharge.VALIDATION_CHOICES)
    operating_unit = BaseInFilter(lookup_expr="in", field_name="operating_unit")
    station_id = BaseInFilter(lookup_expr="in", field_name="station_id")

    def filter_not_validated(self, queryset, name, value):
        if value:
            return queryset.exclude(validated_by=ElecProvisionCertificateQualicharge.BOTH)
        return queryset

    class Meta:
        model = ElecProvisionCertificateQualicharge
        fields = [
            "cpo",
            "year",
            "validated_by",
            "not_validated",
            "operating_unit",
            "station_id",
            "date_from",
        ]

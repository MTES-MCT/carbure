from django_filters import BooleanFilter, FilterSet, NumberFilter

from elec.models import ElecProvisionCertificateQualicharge


class ProvisionCertificateQualichargeFilter(FilterSet):
    entity_id = NumberFilter(field_name="cpo", lookup_expr="exact")
    not_validated = BooleanFilter(method="filter_not_validated")

    def filter_not_validated(self, queryset, name, value):
        if value:
            return queryset.exclude(validated_by=ElecProvisionCertificateQualicharge.BOTH)
        return queryset

    class Meta:
        model = ElecProvisionCertificateQualicharge
        fields = [
            "entity_id",
            "year",
            "validated_by",
            "not_validated",
            "operating_unit",
            "station_id",
            "date_from",
        ]

from django_filters import BaseInFilter, BooleanFilter, FilterSet, MultipleChoiceFilter

from elec.models import ElecProvisionCertificateQualicharge


class ProvisionCertificateQualichargeFilter(FilterSet):
    cpo = BaseInFilter(field_name="cpo__name", lookup_expr="in")
    not_validated = BooleanFilter(method="filter_not_validated")
    validated_by = MultipleChoiceFilter(choices=ElecProvisionCertificateQualicharge.VALIDATION_CHOICES)
    operating_unit = BaseInFilter(lookup_expr="in", field_name="operating_unit")
    station_id = BaseInFilter(lookup_expr="in", field_name="station_id")
    group_by = MultipleChoiceFilter(
        choices=[("operating_unit", "operating_unit")], field_name="group_by", method="filter_group_by"
    )
    date_from = BaseInFilter(lookup_expr="in", field_name="date_from")

    def filter_not_validated(self, queryset, name, value):
        if value:
            return queryset.exclude(validated_by=ElecProvisionCertificateQualicharge.BOTH)
        return queryset

    def filter_group_by(self, queryset, name, value):
        if "operating_unit" in value:
            from django.db.models import Sum

            return (
                queryset.values(
                    "cpo__id",
                    "cpo__name",
                    "cpo__entity_type",
                    "cpo__registration_id",
                    "operating_unit",
                    "date_from",
                    "date_to",
                    "year",
                )
                .annotate(energy_amount=Sum("energy_amount"))
                .order_by("cpo__id", "operating_unit", "date_from")
            )
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

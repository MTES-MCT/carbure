import django_filters

from elec.models import ElecChargePointApplication


class ElecChargePointApplicationFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name="created_at__year", label="Transfer date year")
    status = django_filters.ChoiceFilter(choices=ElecChargePointApplication.STATUSES)

    cpo = django_filters.BaseInFilter(field_name="cpo__name", lookup_expr="in")
    company_id = django_filters.BaseInFilter(field_name="cpo__id")

    class Meta:
        model = ElecChargePointApplication
        fields = ["status", "year", "cpo", "company_id"]

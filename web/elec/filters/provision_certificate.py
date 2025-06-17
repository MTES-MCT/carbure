from django_filters import ChoiceFilter, FilterSet

from elec.models import ElecProvisionCertificate


class ProvisionCertificateFilter(FilterSet):
    source = ChoiceFilter(
        field_name="source",
        choices=ElecProvisionCertificate.SOURCES,
        lookup_expr="iexact",
    )

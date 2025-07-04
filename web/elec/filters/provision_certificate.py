from django_filters import ChoiceFilter, FilterSet, NumberFilter

from elec.models import ElecProvisionCertificate


class ProvisionCertificateFilter(FilterSet):
    source = ChoiceFilter(
        field_name="source",
        choices=ElecProvisionCertificate.SOURCES,
        lookup_expr="iexact",
    )
    entity_id = NumberFilter(field_name="cpo", lookup_expr="exact")

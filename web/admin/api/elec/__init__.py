from django.urls import path, include

from admin.api.elec.provision_certificate_filters import get_provision_certificate_filters


from .years import get_years
from .snapshot import get_snapshot
from .import_provision_certificates import import_provision_certificate_excel
from .provision_certificates import get_provision_certificates

urlpatterns = [
    path("years", get_years, name="admin-elec-years"),
    path("snapshot", get_snapshot, name="admin-elec-snapshot"),
    path("import-provision-certificates", import_provision_certificate_excel, name="admin-elec-import-provision-certs"),
    path("provision-certificates", get_provision_certificates, name="admin-elec-get-provision-certificates"),
    path(
        "provision-certificate-filters", get_provision_certificate_filters, name="admin-elec-provision-certificates-filters"
    ),
]

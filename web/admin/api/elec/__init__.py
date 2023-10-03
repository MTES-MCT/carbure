from django.urls import path, include


from .years import get_years
from .snapshot import get_snapshot
from .import_provision_certificates import import_provision_certificate_excel
from .provision_certificates import get_provision_certificates
from .provision_certificate_filters import get_provision_certificate_filters
from .transfer_certificates import get_transfer_certificates
from .transfer_certificate_filters import get_transfer_certificate_filters
from .transfer_certificate_details import get_transfer_certificate_details


urlpatterns = [
    path("years", get_years, name="admin-elec-years"),
    path("snapshot", get_snapshot, name="admin-elec-snapshot"),
    path("import-provision-certificates", import_provision_certificate_excel, name="admin-elec-import-provision-certs"),
    path("provision-certificates", get_provision_certificates, name="admin-elec-get-provision-certificates"),
    path(
        "provision-certificate-filters", get_provision_certificate_filters, name="admin-elec-provision-certificate-filters"
    ),
    path("transfer-certificates", get_transfer_certificates, name="admin-elec-get-transfer-certificates"),
    path(
        "transfer-certificate-filters", get_transfer_certificate_filters, name="admin-elec-get-transfer-certificate-filters"
    ),
    path(
        "transfer-certificate-details", get_transfer_certificate_details, name="admin-elec-get-transfer-certificate-details"
    ),
]

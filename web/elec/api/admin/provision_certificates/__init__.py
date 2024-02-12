from django.urls import path
from .import_provision_certificates import import_provision_certificate_excel
from .provision_certificates import get_provision_certificates
from .provision_certificate_filters import get_provision_certificate_filters

from .provision_certificate_details import get_provision_certificate_details

urlpatterns = [
    path("", get_provision_certificates, name="admin-elec-get-provision-certificates"),
    path("import-certificates", import_provision_certificate_excel, name="admin-elec-provision-certs-import"),
    path(
        "filters",
        get_provision_certificate_filters,
        name="admin-elec-provision-certificates-filters",
    ),
    path(
        "provision-certificate-details",
        get_provision_certificate_details,
        name="admin-elec-provision-certificates-details",
    ),
]

from django.urls import path

from .years import get_years
from .snapshot import get_snapshot
from .create_transfer_certificate import create_transfer_certificate
from .cancel_transfer_certificate import cancel_transfer_certificate
from .provision_certificates import get_provision_certificates
from .provision_certificate_filters import get_provision_certificate_filters
from .transfer_certificates import get_transfer_certificates
from .transfer_certificate_filters import get_transfer_certificate_filters
from .clients import get_clients

urlpatterns = [
    # overview
    path("years", get_years, name="elec-cpo-years"),
    path("snapshot", get_snapshot, name="elec-cpo-snapshot"),
    path("create-transfer-certificate", create_transfer_certificate, name="elec-cpo-create-transfer-certificate"),
    path("cancel-transfer-certificate", cancel_transfer_certificate, name="elec-cpo-cancel-transfer-certificate"),
    path("provision-certificates", get_provision_certificates, name="elec-cpo-get-provision-certificates"),
    path("provision-certificate-filters", get_provision_certificate_filters, name="elec-cpo-provision-certificate-filters"),
    path("transfer-certificates", get_transfer_certificates, name="elec-cpo-get-transfer-certificates"),
    path("transfer-certificate-filters", get_transfer_certificate_filters, name="elec-cpo-get-transfer-certificate-filters"),
    path("clients", get_clients, name="elec-cpo-clients"),
]

from django.urls import path

from .years import get_years
from .snapshot import get_snapshot
from .accept_transfer_certificate import accept_transfer_certificate
from .reject_transfer_certificate import reject_transfer_certificate
from .transfer_certificates import get_transfer_certificates
from .transfer_certificate_filters import get_transfer_certificate_filters
from .transfer_certificate_details import get_transfer_certificate_details

urlpatterns = [
    # overview
    path("years", get_years, name="elec-operator-years"),
    path("snapshot", get_snapshot, name="elec-operator-snapshot"),
    path("accept-transfer-certificate", accept_transfer_certificate, name="elec-operator-accept-transfer-certificate"),
    path("reject-transfer-certificate", reject_transfer_certificate, name="elec-operator-reject-transfer-certificate"),
    path("transfer-certificates", get_transfer_certificates, name="elec-operator-get-transfer-certificates"),
    path(
        "transfer-certificate-filters",
        get_transfer_certificate_filters,
        name="elec-operator-get-transfer-certificate-filters",
    ),
    path(
        "transfer-certificate-details",
        get_transfer_certificate_details,
        name="elec-operator-get-transfer-certificate-details",
    ),
]

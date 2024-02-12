from django.urls import path

from .transfer_certificates import get_transfer_certificates
from .transfer_certificate_filters import get_transfer_certificate_filters
from .transfer_certificate_details import get_transfer_certificate_details

urlpatterns = [
    path("", get_transfer_certificates, name="admin-elec-get-transfer-certificates"),
    path(
        "transfer-certificate-details",
        get_transfer_certificate_details,
        name="admin-elec-transfer-certificates-details",
    ),
    path(
        "filters",
        get_transfer_certificate_filters,
        name="admin-elec-transfer-certificate-filters",
    ),
]

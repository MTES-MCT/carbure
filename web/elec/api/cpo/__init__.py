from django.urls import include, path

from .certificate_years import get_certificate_years
from .certificate_snapshot import get_certificate_snapshot
from .charge_point_snapshot import get_charge_point_snapshot
from .create_transfer_certificate import create_transfer_certificate
from .cancel_transfer_certificate import cancel_transfer_certificate
from .provision_certificates import get_provision_certificates
from .provision_certificate_filters import get_provision_certificate_filters
from .provision_certificate_details import get_provision_certificate_details
from .transfer_certificates import get_transfer_certificates
from .transfer_certificate_filters import get_transfer_certificate_filters
from .transfer_certificate_details import get_transfer_certificate_details
from .clients import get_clients

urlpatterns = [
    # overview
    path("certificate-years", get_certificate_years, name="elec-cpo-certificate-years"),
    path("certificate-snapshot", get_certificate_snapshot, name="elec-cpo-certificate-snapshot"),
    path("charge-point-snapshot", get_charge_point_snapshot, name="elec-cpo-charge-point-snapshot"),
    path("create-transfer-certificate", create_transfer_certificate, name="elec-cpo-create-transfer-certificate"),
    path("cancel-transfer-certificate", cancel_transfer_certificate, name="elec-cpo-cancel-transfer-certificate"),
    path("provision-certificates", get_provision_certificates, name="elec-cpo-get-provision-certificates"),
    path("provision-certificate-filters", get_provision_certificate_filters, name="elec-cpo-provision-certificate-filters"),
    path(
        "provision-certificate-details", get_provision_certificate_details, name="elec-cpo-get-provision-certificate-details"
    ),
    path("transfer-certificates", get_transfer_certificates, name="elec-cpo-get-transfer-certificates"),
    path("transfer-certificate-filters", get_transfer_certificate_filters, name="elec-cpo-get-transfer-certificate-filters"),
    path("transfer-certificate-details", get_transfer_certificate_details, name="elec-cpo-get-transfer-certificate-details"),
    path("clients", get_clients, name="elec-cpo-clients"),
    path("charge-points/", include("elec.api.cpo.charge_points")),
    path("meter-readings/", include("elec.api.cpo.meter_readings")),
    path("meters/", include("elec.api.cpo.meters")),
]

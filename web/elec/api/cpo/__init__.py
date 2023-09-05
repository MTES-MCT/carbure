from django.urls import path


from .snapshot import get_snapshot
from .transfer_provision_certificate import transfer_provision_certificate
from .cancel_transfer_certificate import cancel_transfer_certificate

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="elec-cpo-snapshot"),
    path("transfer-provision-certificate", transfer_provision_certificate, name="elec-cpo-transfer-provision-certificate"),
    path("cancel-transfer-certificate", cancel_transfer_certificate, name="elec-cpo-cancel-transfer-certificate"),
]

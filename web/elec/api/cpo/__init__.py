from django.urls import path


from .snapshot import get_snapshot
from .create_transfer_certificate import create_transfer_certificate
from .cancel_transfer_certificate import cancel_transfer_certificate

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="elec-cpo-snapshot"),
    path("create-transfer-certificate", create_transfer_certificate, name="elec-cpo-create-transfer-certificate"),
    path("cancel-transfer-certificate", cancel_transfer_certificate, name="elec-cpo-cancel-transfer-certificate"),
]

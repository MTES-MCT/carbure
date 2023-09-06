from django.urls import path

from .snapshot import get_snapshot
from .accept_transfer_certificate import accept_transfer_certificate
from .reject_transfer_certificate import reject_transfer_certificate

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="elec-operator-snapshot"),
    path("accept-transfer-certificate", accept_transfer_certificate, name="elec-operator-accept-transfer-certificate"),
    path("reject-transfer-certificate", reject_transfer_certificate, name="elec-operator-reject-transfer-certificate"),
]

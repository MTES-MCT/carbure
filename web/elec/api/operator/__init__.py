from django.urls import path

from .snapshot import get_snapshot
from .reject_transfer_certificate import reject_transfer_certificate

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="elec-operator-snapshot"),
    path("reject-transfer-certificate", reject_transfer_certificate, name="elec-operator-reject-transfer-certificate"),
]

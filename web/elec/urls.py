from django.urls import path

from rest_framework_nested.routers import SimpleRouter

from .api import urlpatterns as api_urlpatterns
from .views import ProvisionCertificateViewSet, TransferCertificateViewSet, get_clients, get_snapshot, get_years

router = SimpleRouter()
router.register("provision-certificates", ProvisionCertificateViewSet, basename="provision-certificates")
router.register("transfer-certificates", TransferCertificateViewSet, basename="transfer-certificates")
router.register(
    "provision-certificates-qualicharge",
    ElecProvisionCertificateQualichargeViewSet,
    basename="elec-provision-certificate-qualicharge",
)

urlpatterns = (
    api_urlpatterns
    + router.urls
    + [
        path("certificates/years/", get_years, name="elec-certificates-years"),
        path("certificates/snapshot/", get_snapshot, name="elec-certificates-snapshot"),
        path("certificates/clients/", get_clients, name="elec-certificates-clients"),
    ]
)

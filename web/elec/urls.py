from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import ProvisionCertificateViewSet, TransferCertificateViewSet, get_clients, get_snapshot, get_years

router = SimpleRouter()
router.register("provision-certificates", ProvisionCertificateViewSet, basename="provision-certificates")
router.register("transfer-certificates", TransferCertificateViewSet, basename="transfer-certificates")

urlpatterns = [
    path("certificates/years/", get_years, name="elec-certificates-years"),
    path("certificates/snapshot/", get_snapshot, name="elec-certificates-snapshot"),
    path("certificates/clients/", get_clients, name="elec-certificates-clients"),
] + router.urls

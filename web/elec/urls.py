from django.urls import include, path
from rest_framework.routers import DefaultRouter

from elec.views import ElecProvisionCertificateQualichargeViewSet

router = DefaultRouter()
router.register(
    r"provision-certificates-qualicharge",
    ElecProvisionCertificateQualichargeViewSet,
    basename="elec-provision-certificate-qualicharge",
)

urlpatterns = [
    path("", include(router.urls)),
]

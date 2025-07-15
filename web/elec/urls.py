from rest_framework_nested.routers import SimpleRouter

from elec.views import ElecProvisionCertificateQualichargeViewSet

router = SimpleRouter()
router.register(
    "provision-certificates-qualicharge",
    ElecProvisionCertificateQualichargeViewSet,
    basename="elec-provision-certificate-qualicharge",
)

urlpatterns = router.urls

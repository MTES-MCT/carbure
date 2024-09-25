from django.urls import include, path
from rest_framework_nested.routers import SimpleRouter

from elec.views import (
    ElecChargePointApplicationViewSet,
    ElecChargePointViewSet,
    TransfertCertificateViewSet,
)

router = SimpleRouter()
router.register(
    "transfer-certificates",
    TransfertCertificateViewSet,
    basename="elect-transfer-certificates",
)
router.register(
    "charge-points",
    ElecChargePointViewSet,
    basename="elect-charge-points",
)
router.register(
    "applications",
    ElecChargePointApplicationViewSet,
    basename="applications",
)
urlpatterns = [
    path("cpo/", include("elec.api.cpo")),
    path("operator/", include("elec.api.operator")),
    path("admin/", include("elec.api.admin")),
    path("auditor/", include("elec.api.auditor")),
] + router.urls

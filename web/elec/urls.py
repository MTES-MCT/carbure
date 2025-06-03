from django.urls import include, path
from rest_framework.routers import DefaultRouter

from elec.views import ElecProvisionCertificateViewSet

router = DefaultRouter()
router.register(r"provision-certificates", ElecProvisionCertificateViewSet, basename="elec-provision-certificate")

urlpatterns = [
    path("", include(router.urls)),
]

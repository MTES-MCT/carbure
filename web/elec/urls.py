# from django.urls import path
from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import ProvisionCertificateViewSet, get_years

router = SimpleRouter()
router.register("provision-certificates", ProvisionCertificateViewSet, basename="provision-certificates")

urlpatterns = [
    path("certificates/years/", get_years, name="elec-certificates-years"),
] + router.urls

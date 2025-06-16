# from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import ProvisionCertificateViewSet

router = SimpleRouter()
router.register("provision-certificates", ProvisionCertificateViewSet, basename="provision-certificates")

urlpatterns = [] + router.urls

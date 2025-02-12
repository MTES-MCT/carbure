from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import AgreementViewSet, ApplicationViewSet, get_snapshot

router = SimpleRouter()
router.register("applications", ApplicationViewSet, basename="double-counting-applications")
router.register("agreements", AgreementViewSet, basename="double-counting-agreements")
urlpatterns = [
    path("snapshot/", get_snapshot, name="double-counting-snapshot"),
] + router.urls

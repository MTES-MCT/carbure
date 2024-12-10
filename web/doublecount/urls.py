from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import AgreementViewSet, ApplicationViwSet, get_snapshot

router = SimpleRouter()
router.register("applications", ApplicationViwSet, basename="double-counting-applications")
router.register("agreements", AgreementViewSet, basename="double-counting-agreements")
urlpatterns = [
    path("snapshot/", get_snapshot, name="saf-snapshot"),
] + router.urls

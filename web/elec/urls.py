from rest_framework_nested.routers import SimpleRouter

from .views import ChargePointViewSet

router = SimpleRouter()
router.register("charge-points", ChargePointViewSet, basename="charge-points")

urlpatterns = router.urls

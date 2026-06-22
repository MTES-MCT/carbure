from rest_framework.routers import SimpleRouter

from stock_poc.views import ActionViewSet

router = SimpleRouter()
router.register("actions", ActionViewSet, basename="stock-poc-actions")

urlpatterns = router.urls

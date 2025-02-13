from rest_framework_nested.routers import SimpleRouter

from .views import (
    # OperationDetailViewSet,
    OperationViewSet,
)

router = SimpleRouter()
router.register("operations", OperationViewSet, basename="operations")
# router.register("operations/detail", OperationDetailViewSet, basename="operation-details")

urlpatterns = router.urls

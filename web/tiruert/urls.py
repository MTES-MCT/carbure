from rest_framework_nested.routers import SimpleRouter

from .views import (
    ObjectiveViewSet,
    OperationViewSet,
)

router = SimpleRouter()
router.register("operations", OperationViewSet, basename="operations")
router.register("objectives", ObjectiveViewSet, basename="objectives")

urlpatterns = router.urls

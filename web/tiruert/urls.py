from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    ElecOperationViewSet,
    ObjectiveViewSet,
    OperationViewSet,
)

router = SimpleRouter()
router.register("operations", OperationViewSet, basename="operations")
router.register("elec_operations", ElecOperationViewSet, basename="elec-operations")

objectives = ObjectiveViewSet.as_view({"get": "get_objectives"})

urlpatterns = router.urls + [
    path("objectives/", objectives, name="get-objectives"),
]

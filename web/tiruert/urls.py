from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    ObjectiveViewSet,
    OperationViewSet,
)

router = SimpleRouter()
router.register("operations", OperationViewSet, basename="operations")

objectives = ObjectiveViewSet.as_view({"get": "get_objectives"})

urlpatterns = router.urls + [
    path("objectives/", objectives, name="get-objectives"),
]

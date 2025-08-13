from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    BiomethaneContractAmendmentViewSet,
    BiomethaneContractViewSet,
)
from .views.production_unit import (
    BiomethaneDigestateStorageViewSet,
    BiomethaneProductionUnitViewSet,
)

router = SimpleRouter()
router.register(
    "contract/amendments",
    BiomethaneContractAmendmentViewSet,
    basename="biomethane-contract-amendment",
)
router.register(
    "digestate-storage",
    BiomethaneDigestateStorageViewSet,
    basename="biomethane-digestate-storage",
)

contract_viewset = BiomethaneContractViewSet.as_view(
    {
        "get": "retrieve",
        "post": "create",
        "patch": "update",
    }
)

production_unit_viewset = BiomethaneProductionUnitViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

urlpatterns = [
    path("contract/", contract_viewset, name="biomethane-contract"),
    path("production-unit/", production_unit_viewset, name="biomethane-production-unit"),
    *router.urls,
]

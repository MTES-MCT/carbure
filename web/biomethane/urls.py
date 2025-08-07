from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views.entity_config_contract import (
    BiomethaneEntityConfigContractAmendmentViewSet,
    BiomethaneEntityConfigContractViewSet,
)

router = SimpleRouter()
router.register(
    "contract/amendments",
    BiomethaneEntityConfigContractAmendmentViewSet,
    basename="biomethane-entity-config-contract-amendment",
)

contract_viewset = BiomethaneEntityConfigContractViewSet.as_view(
    {
        "get": "contract_get",
        "post": "create",
        "patch": "contract_patch",
    }
)

urlpatterns = [
    path("contract/", contract_viewset, name="biomethane-entity-config-contract"),
    *router.urls,
]

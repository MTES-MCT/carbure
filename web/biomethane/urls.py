from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views.entity_config_contract.entity_config_contract import BiomethaneEntityConfigContractViewSet

router = SimpleRouter()

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

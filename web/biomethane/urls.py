from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views.entity_config_contract.entity_config_contract import BiomethaneEntityConfigContractViewSet

router = SimpleRouter()
router.register("contract", BiomethaneEntityConfigContractViewSet, basename="entity-config-contract")

# URL for patching a contract without an ID
contract_viewset = BiomethaneEntityConfigContractViewSet.as_view({"patch": "partial_update"})

urlpatterns = [
    path("contract/", contract_viewset, name="contract-patch"),
    *router.urls,
]

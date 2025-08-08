from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    BiomethaneContractAmendmentViewSet,
    BiomethaneContractViewSet,
    BiomethaneInjectionSiteViewSet,
)

router = SimpleRouter()
router.register(
    "contract/amendments",
    BiomethaneContractAmendmentViewSet,
    basename="biomethane-contract-amendment",
)

contract_viewset = BiomethaneContractViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

injection_site_viewset = BiomethaneInjectionSiteViewSet.as_view(
    {
        "get": "retrieve",
        "post": "create",
        "put": "update",
    }
)

urlpatterns = [
    path("contract/", contract_viewset, name="biomethane-contract"),
    path("injection-site/", injection_site_viewset, name="biomethane-injection-site"),
    *router.urls,
]

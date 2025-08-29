from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    BiomethaneContractAmendmentViewSet,
    BiomethaneContractViewSet,
    BiomethaneInjectionSiteViewSet,
)
from .views.digestate.digestate import BiomethaneDigestateViewSet
from .views.digestate.spreading import BiomethaneDigestateSpreadingViewSet
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
router.register(
    "digestate/spreading",
    BiomethaneDigestateSpreadingViewSet,
    basename="biomethane-digestate-spreading",
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
        "put": "upsert",
    }
)

production_unit_viewset = BiomethaneProductionUnitViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

digestate_viewset = BiomethaneDigestateViewSet.as_view(
    {
        "get": "retrieve",
        "put": "upsert",
    }
)

digestate_years_viewset = BiomethaneDigestateViewSet.as_view(
    {
        "get": "get_years",
    }
)

digestate_validate_viewset = BiomethaneDigestateViewSet.as_view(
    {
        "post": "validate_digestate",
    }
)

urlpatterns = [
    path("contract/", contract_viewset, name="biomethane-contract"),
    path("injection-site/", injection_site_viewset, name="biomethane-injection-site"),
    path("production-unit/", production_unit_viewset, name="biomethane-production-unit"),
    path("digestate/", digestate_viewset, name="biomethane-digestate"),
    path("digestate/years/", digestate_years_viewset, name="biomethane-digestate-years"),
    path("digestate/validate/", digestate_validate_viewset, name="biomethane-digestate-validate"),
    *router.urls,
]

from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    ElecOperationViewSet,
    MacFossilFuelExportViewSet,
    ObjectiveViewSet,
    OperationViewSet,
    curent_declaration_period,
    declaration_period_years,
)

router = SimpleRouter()
router.register("operations", OperationViewSet, basename="operations")
router.register("elec-operations", ElecOperationViewSet, basename="elec-operations")
router.register("mac-fossil-fuel", MacFossilFuelExportViewSet, basename="mac-fossil-fuel")

objectives = ObjectiveViewSet.as_view({"get": "get_objectives"})
agregated_objectives_admin_view = ObjectiveViewSet.as_view({"get": "get_agregated_objectives_admin_view"})
objectives_admin_view = ObjectiveViewSet.as_view({"get": "get_objectives_admin_view"})

urlpatterns = router.urls + [
    path("objectives/", objectives, name="get-objectives"),
    path("admin-objectives/", agregated_objectives_admin_view, name="get-admin-objectives"),
    path("admin-objectives-entity/", objectives_admin_view, name="get-admin-objectives-entity"),
    path("declaration-period/", curent_declaration_period, name="declaration-period-is-open"),
    path("declaration-period/years/", declaration_period_years, name="declaration-period-years"),
]

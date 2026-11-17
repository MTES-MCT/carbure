from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from entity.views import (
    AdminUsersViewSet,
    DepotViewSet,
    EntityCertificateViewSet,
    EntityViewSet,
    NotificationViewSet,
    ProductionSiteViewSet,
    UserViewSet,
    add_company_view,
    search_company_view,
)
from entity.views.energy_installation import EnergyInstallationView

router = SimpleRouter()
router.register("users", UserViewSet, basename="api-entity-users")
router.register("admin-users", AdminUsersViewSet, basename="api-entity-admin-users")
router.register("certificates", EntityCertificateViewSet, basename="api-entity-certificates")
router.register("depots", DepotViewSet, basename="api-entity-depots")
router.register("notifications", NotificationViewSet, basename="api-entity-notifications")
router.register("production-sites", ProductionSiteViewSet, basename="api-entity-production-sites")
router.register(r"", EntityViewSet, basename="entity")

urlpatterns = [
    path("energy-installation/", EnergyInstallationView.as_view(), name="energy-installation"),
    path(
        "search-company/",
        search_company_view,
        name="api-entity-registration-search-company",
    ),
    path("add-company", add_company_view, name="api-entity-registration-add-company"),
]

urlpatterns += router.urls

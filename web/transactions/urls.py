from django.urls import include, path
from rest_framework_nested.routers import SimpleRouter

from transactions.api import get_snapshot, get_years

from .views import LotsViewSet, StockViewSet, api_snapshot, api_years

router = SimpleRouter()
router.register("api-lots", LotsViewSet, basename="transactions-api-lots")
router.register("api-stocks", StockViewSet, basename="transactions-api-stocks")

urlpatterns = [
    path("api-snapshot", api_snapshot, name="transactions-api-snapshot"),
    path("api-years", api_years, name="transactions-api-years"),
    path("snapshot", get_snapshot, name="transactions-snapshot"),
    path("years", get_years, name="transactions-years"),
    path("audit/", include("transactions.api.audit")),
    path("admin/", include("transactions.api.admin")),
    path("lots/", include("transactions.api.lots")),
    path("stocks/", include("transactions.api.stocks")),
    path("declarations/", include("transactions.api.declarations")),
] + router.urls

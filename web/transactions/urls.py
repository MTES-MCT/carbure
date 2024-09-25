from django.urls import include, path
from rest_framework_nested.routers import SimpleRouter

from transactions.api import get_snapshot, get_years

from .views import LotsViewSet

router = SimpleRouter()
router.register("api-lots", LotsViewSet, basename="transactions-api-lots")

urlpatterns = [
    path("snapshot", get_snapshot, name="transactions-snapshot"),
    path("years", get_years, name="transactions-years"),
    path("audit/", include("transactions.api.audit")),
    path("admin/", include("transactions.api.admin")),
    path("lots/", include("transactions.api.lots")),
    path("stocks/", include("transactions.api.stocks")),
    path("declarations/", include("transactions.api.declarations")),
] + router.urls

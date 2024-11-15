from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import LotsViewSet, StockViewSet, api_snapshot, api_years

router = SimpleRouter()
router.register("lots", LotsViewSet, basename="transactions-lots")
router.register("stocks", StockViewSet, basename="transactions-stocks")

urlpatterns = [
    path("snapshot", api_snapshot, name="transactions-snapshot"),
    path("years", api_years, name="transactions-years"),
] + router.urls

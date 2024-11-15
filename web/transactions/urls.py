from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import LotsViewSet, StockViewSet, api_snapshot, api_years

router = SimpleRouter()
router.register("lots", LotsViewSet, basename="v2-transactions-lots")
router.register("stocks", StockViewSet, basename="v2-transactions-stocks")

urlpatterns = [
    path("snapshot", api_snapshot, name="v2-transactions-snapshot"),
    path("years", api_years, name="v2-transactions-years"),
] + router.urls

from django.urls import path
from rest_framework_nested.routers import SimpleRouter

from .views import (
    ClientViewSet,
    SafTicketSourceViewSet,
    SafTicketViewSet,
    get_snapshot,
    get_years,
)

router = SimpleRouter()
router.register("tickets", SafTicketViewSet, basename="saf-tickets")
router.register("ticket-sources", SafTicketSourceViewSet, basename="saf-ticket-sources")
router.register("clients", ClientViewSet, basename="clients")
urlpatterns = [
    path("years/", get_years, name="saf-years"),
    path("snapshot/", get_snapshot, name="saf-snapshot"),
] + router.urls

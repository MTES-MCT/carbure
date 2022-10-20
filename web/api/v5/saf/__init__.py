from django.urls import path

from .years import get_years
from .snapshot import get_snapshot
from .ticket_sources import get_ticket_sources
from .tickets import get_tickets

urlpatterns = [
    path("years", get_years, name="api-v5-saf-years"),
    path("snapshot", get_snapshot, name="api-v5-saf-snapshot"),
    path("ticket-sources", get_ticket_sources, name="api-v5-saf-ticket-sources"),
    path("tickets", get_tickets, name="api-v5-saf-tickets"),
]

from django.urls import path

from .clients import get_clients
from .years import get_years
from .snapshot import get_snapshot
from .ticket_sources import get_ticket_sources
from .ticket_source_details import get_ticket_source_details
from .tickets import get_tickets
from .ticket_details import get_ticket_details
from .ticket_source_filters import get_ticket_source_filters
from .assign_ticket import assign_ticket

urlpatterns = [
    # overview
    path("years", get_years, name="api-v5-saf-years"),
    path("snapshot", get_snapshot, name="api-v5-saf-snapshot"),
    # ticket sources
    path("ticket-sources", get_ticket_sources, name="api-v5-saf-ticket-sources"),
    path("ticket-sources/filters", get_ticket_source_filters, name="api-v5-saf-ticket-source-filters"),
    path("ticket-sources/details", get_ticket_source_details, name="api-v5-saf-ticket-source-details"),
    # tickets
    path("tickets", get_tickets, name="api-v5-saf-tickets"),
    path("tickets/details", get_ticket_details, name="api-v5-saf-ticket-details"),
    # ticket actions
    path("assign-ticket", assign_ticket, name="api-v5-saf-assign-ticket"),
    # autocomplete helpers
    path("clients", get_clients, name="api-v5-saf-clients"),
]

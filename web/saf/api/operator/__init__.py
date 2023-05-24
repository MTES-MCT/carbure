from django.urls import path

from .clients import get_clients
from .years import get_years
from .snapshot import get_snapshot
from .ticket_sources import get_ticket_sources
from .ticket_source_details import get_ticket_source_details
from .tickets import get_tickets
from .ticket_details import get_ticket_details
from .ticket_source_filters import get_ticket_source_filters
from .ticket_filters import get_ticket_filters
from .assign_ticket import assign_ticket
from .grouped_assign_ticket import grouped_assign_ticket
from .cancel_ticket import cancel_ticket
from .reject_ticket import reject_ticket
from .credit_ticket_source import credit_ticket_source

urlpatterns = [
    # overview
    path("years", get_years, name="saf-operator-years"),
    path("snapshot", get_snapshot, name="saf-operator-snapshot"),
    # ticket sources
    path("ticket-sources", get_ticket_sources, name="saf-operator-ticket-sources"),
    path("ticket-sources/filters", get_ticket_source_filters, name="saf-operator-ticket-source-filters"),
    path("ticket-sources/details", get_ticket_source_details, name="saf-operator-ticket-source-details"),
    # tickets
    path("tickets", get_tickets, name="saf-operator-tickets"),
    path("tickets/filters", get_ticket_filters, name="saf-operator-ticket-filters"),
    path("tickets/details", get_ticket_details, name="saf-operator-ticket-details"),
    # ticket actions
    path("assign-ticket", assign_ticket, name="saf-operator-assign-ticket"),
    path("grouped-assign-ticket", grouped_assign_ticket, name="saf-operator-grouped-assign-ticket"),
    path("cancel-ticket", cancel_ticket, name="saf-operator-cancel-ticket"),
    path("reject-ticket", reject_ticket, name="saf-operator-reject-ticket"),
    path("credit-ticket-source", credit_ticket_source, name="saf-operator-credit-ticket-source"),
    # autocomplete helpers
    path("clients", get_clients, name="saf-operator-clients"),
]

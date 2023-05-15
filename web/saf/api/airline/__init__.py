from django.urls import path

from .years import get_years
from .snapshot import get_snapshot
from .tickets import get_tickets
from .ticket_details import get_ticket_details
from .ticket_filters import get_ticket_filters
from .accept_ticket import accept_ticket
from .reject_ticket import reject_ticket

urlpatterns = [
    # overview
    path("years", get_years, name="saf-airline-years"),
    path("snapshot", get_snapshot, name="saf-airline-snapshot"),
    # tickets
    path("tickets", get_tickets, name="saf-airline-tickets"),
    path("tickets/filters", get_ticket_filters, name="saf-airline-ticket-filters"),
    path("tickets/details", get_ticket_details, name="saf-airline-ticket-details"),
    # ticket actions
    path("accept-ticket", accept_ticket, name="saf-airline-accept-ticket"),
    path("reject-ticket", reject_ticket, name="saf-airline-reject-ticket"),
]

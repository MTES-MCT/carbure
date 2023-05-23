from django.urls import path
from .lots import get_lots
from .summary import get_lots_summary
from .filters import get_lots_filters
from .details import get_lot_details
from .toggle_warning import toggle_warning
from .pin import toggle_pin
from .comment import add_comment


urlpatterns = [
    path("", get_lots, name="admin-controls-lots"),
    path("summary", get_lots_summary, name="admin-controls-lots-summary"),
    path("filters", get_lots_filters, name="admin-controls-lots-filters"),
    path("details", get_lot_details, name="admin-controls-lot-details"),
    path("toggle-warning", toggle_warning, name="admin-controls-lots-toggle-warning"),
    path("pin", toggle_pin, name="admin-controls-lots-pin"),
    path("comment", add_comment, name="admin-controls-lots-comment"),
]

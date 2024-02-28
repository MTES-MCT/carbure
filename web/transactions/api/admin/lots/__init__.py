from django.urls import path
from .lots import get_lots
from .summary import get_lots_summary
from .filters import get_lots_filters
from .details import get_lot_details
from .toggle_warning import toggle_warning
from .pin import toggle_pin
from .comment import add_comment
from .delete_many import delete_many
from .update_many import update_many


urlpatterns = [
    path("", get_lots, name="transactions-admin-lots"),
    path("comment", add_comment, name="transactions-admin-lots-comment"),
    path("delete-many", delete_many, name="transactions-admin-lots-delete-many"),
    path("details", get_lot_details, name="admin-controls-lot-details"),
    path("filters", get_lots_filters, name="transactions-admin-lots-filters"),
    path("pin", toggle_pin, name="transactions-admin-lots-pin"),
    path("summary", get_lots_summary, name="transactions-admin-lots-summary"),
    path("toggle-warning", toggle_warning, name="transactions-admin-lots-toggle-warning"),
    path("update-many", update_many, name="transactions-admin-lots-update-many"),
]

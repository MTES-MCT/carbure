from django.urls import path

# from .add import add_lot
from .update import update_lot
from .request_fix import request_fix
from .submit_fix import submit_fix
from .approve_fix import approve_fix
from .lots import get_lots
from .add import add_lot
from .filters import get_lots_filters
from .details import get_lot_details
from .summary import get_lots_summary

urlpatterns = [
    path("", get_lots, name="transactions-lots"),
    path("filters", get_lots_filters, name="transactions-lots-filters"),
    path("details", get_lot_details, name="transactions-lots-details"),
    path("summary", get_lots_summary, name="transactions-lots-summary"),
    path("add", add_lot, name="transactions-lots-add"),
    path("update", update_lot, name="transactions-lots-update"),
    path("request-fix", request_fix, name="transactions-lots-request-fix"),
    path("submit-fix", submit_fix, name="transactions-lots-submit-fix"),
    path("approve-fix", approve_fix, name="transactions-lots-approve-fix"),
]

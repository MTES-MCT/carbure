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
from .add_excel import add_excel
from .duplicate import duplicate_lot
from .send import lots_send
from .delete import lots_delete
from .comment import add_comment
from .reject import reject_lot
from .accept_in_stock import accept_in_stock
from .accept_trading import accept_trading
from .accept_processing import accept_processing
from .accept_blending import accept_blending
from .accept_export import accept_export
from .accept_direct_delivery import accept_direct_delivery
from .cancel_accept import cancel_accept_lots
from .accept_release_for_consumption import accept_rfc
from .template import get_template

urlpatterns = [
    path("", get_lots, name="transactions-lots"),
    path("filters", get_lots_filters, name="transactions-lots-filters"),
    path("details", get_lot_details, name="transactions-lots-details"),
    path("summary", get_lots_summary, name="transactions-lots-summary"),
    path("add", add_lot, name="transactions-lots-add"),
    path("add-excel", add_excel, name="transactions-lots-add-excel"),
    path("duplicate", duplicate_lot, name="transactions-lots-duplicate"),
    path("send", lots_send, name="transactions-lots-send"),
    path("delete", lots_delete, name="transactions-lots-delete"),
    path("update", update_lot, name="transactions-lots-update"),
    path("request-fix", request_fix, name="transactions-lots-request-fix"),
    path("submit-fix", submit_fix, name="transactions-lots-submit-fix"),
    path("approve-fix", approve_fix, name="transactions-lots-approve-fix"),
    path("comment", add_comment, name="transactions-lots-comment"),
    path("reject", reject_lot, name="transactions-lots-reject"),
    path("accept-in-stock", accept_in_stock, name="transactions-lots-accept-in-stock"),
    path("accept-trading", accept_trading, name="transactions-lots-accept-trading"),
    path(
        "accept-processing",
        accept_processing,
        name="transactions-lots-accept-processing",
    ),
    path("accept-blending", accept_blending, name="transactions-lots-accept-blending"),
    path("accept-export", accept_export, name="transactions-lots-accept-export"),
    path(
        "accept-direct-delivery",
        accept_direct_delivery,
        name="transactions-lots-accept-direct-delivery",
    ),
    path("cancel-accept", cancel_accept_lots, name="transactions-lots-cancel-accept"),
    path(
        "accept-release-for-consumption",
        accept_rfc,
        name="transactions-lots-accept-release-for-consumption",
    ),
    path("template", get_template, name="transactions-lots-template"),
]

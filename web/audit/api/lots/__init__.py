from django.urls import path
from .lots import get_lots
from .summary import get_lots_summary
from .filters import get_lots_filters
from .details import get_lot_details
from .toggle_warning import toggle_warning
from .pin import toggle_pin
from .comment import add_comment
from .mark_as_conform import mark_conform
from .mark_as_nonconform import mark_nonconform

urlpatterns = [
    path("", get_lots, name="audit-lots"),
    path("summary", get_lots_summary, name="audit-lots-summary"),
    path("filters", get_lots_filters, name="audit-lots-filters"),
    path("details", get_lot_details, name="audit-lot-details"),
    path("toggle-warning", toggle_warning, name="audit-lots-toggle-warning"),
    path("pin", toggle_pin, name="audit-lots-pin"),
    path("comment", add_comment, name="audit-lots-comment"),
    path("mark-as-conform", mark_conform, name="audit-lots-mark-as-conform"),
    path("mark-as-nonconform", mark_nonconform, name="audit-lots-mark-as-nonconform"),
]

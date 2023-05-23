from api.v4 import views
from django.urls import path

urlpatterns = [
    # GET
    # path("lots", views.get_lots, name="api-v4-get-lots"),
    # path("lots/summary", views.get_lots_summary, name="api-v4-get-lots-summary"),
    # path("lots/details", views.get_lot_details, name="api-v4-get-lot-details"),
    # path("lots/filters", views.get_lots_filters, name="api-v4-get-lots-filters"),
    # POST
    ### Lot initial life
    # path("lots/add", views.add_lot, name="transactions-lots-add"),
    # path("lots/add-excel", views.add_excel, name="api-v4-add-excel"),
    # path("lots/duplicate", views.duplicate_lot, name="transactions-lots-duplicate"),
    # path("lots/send", views.lots_send, name="transactions-lots-send"),
    # path("lots/delete", views.lots_delete, name="transactions-lots-delete"),
    ### Corrections
    path("lots/comment", views.add_comment, name="api-v4-comment-lots"),
    path("lots/reject", views.reject_lot, name="api-v4-reject-lots"),
    ### Approval
    path(
        "lots/accept-release-for-consumption",
        views.accept_rfc,
        name="api-v4-accept-rfc",
    ),  ### is this necessary? MAC are tagged when they are sent usually
    path("lots/accept-in-stock", views.accept_in_stock, name="api-v4-accept-in-stock"),
    path("lots/accept-trading", views.accept_trading, name="api-v4-accept-trading"),
    path(
        "lots/accept-processing",
        views.accept_processing,
        name="api-v4-accept-processing",
    ),
    path("lots/accept-blending", views.accept_blending, name="api-v4-accept-blending"),
    path("lots/accept-export", views.accept_export, name="api-v4-accept-export"),
    path(
        "lots/accept-direct-delivery",
        views.accept_direct_delivery,
        name="api-v4-accept-direct-delivery",
    ),
    path("lots/cancel-accept", views.cancel_accept_lots, name="api-v4-cancel-accept"),
    ### Warnings
    path("lots/toggle-warning", views.toggle_warning, name="api-v4-toggle-warning"),
    path("lots/recalc-score", views.recalc_score, name="api-v4-recalc-score"),
    path("download-template", views.get_template, name="api-v4-get-template"),
    path(
        "download-template-stock",
        views.get_template_stock,
        name="api-v4-get-template-stock",
    ),
]

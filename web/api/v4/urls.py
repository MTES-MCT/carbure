from api.v4 import admin, auditor, views
from django.urls import path

urlpatterns = [
    # GET
    path("years", views.get_years, name="api-v4-get-years"),
    path("snapshot", views.get_snapshot, name="api-v4-get-snapshot"),
    path("lots", views.get_lots, name="api-v4-get-lots"),
    path("lots/summary", views.get_lots_summary, name="api-v4-get-lots-summary"),
    path("lots/details", views.get_lot_details, name="api-v4-get-lot-details"),
    path("lots/filters", views.get_lots_filters, name="api-v4-get-lots-filters"),
    # POST
    ### Lot initial life
    path("lots/add", views.add_lot, name="api-v4-add-lots"),
    path("lots/add-excel", views.add_excel, name="api-v4-add-excel"),
    path("lots/duplicate", views.duplicate_lot, name="api-v4-duplicate-lot"),
    path("lots/update", views.update_lot, name="api-v4-update-lot"),
    path("lots/send", views.lots_send, name="api-v4-send-lots"),
    path("lots/delete", views.lots_delete, name="api-v4-delete-lots"),
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
    # DECLARATIONS
    path("declarations", views.get_declarations, name="api-v4-get-declarations"),
    path("download-template", views.get_template, name="api-v4-get-template"),
    path(
        "download-template-stock",
        views.get_template_stock,
        name="api-v4-get-template-stock",
    ),
    # ADMIN
    path("admin/years", admin.get_years, name="api-v4-admin-get-years"),
    path("admin/snapshot", admin.get_snapshot, name="api-v4-admin-get-snapshot"),
    path("admin/lots", admin.get_lots, name="api-v4-admin-get-lots"),
    path(
        "admin/lots/summary",
        admin.get_lots_summary,
        name="api-v4-admin-get-lots-summary",
    ),
    path("admin/lots/details", admin.get_lot_details, name="api-v4-admin-get-lot-details"),
    path(
        "admin/lots/filters",
        admin.get_lots_filters,
        name="api-v4-admin-get-lots-filters",
    ),
    path(
        "admin/lots/toggle-warning",
        admin.toggle_warning,
        name="api-v4-admin-toggle-warning",
    ),
    path("admin/lots/pin", admin.toggle_pin, name="api-v4-admin-pin-lots"),
    path("admin/lots/comment", admin.add_comment, name="api-v4-admin-add-comment"),
    path("admin/stocks", admin.get_stocks, name="api-v4-admin-get-stocks"),
    path(
        "admin/stocks/details",
        admin.get_stock_details,
        name="api-v4-admin-get-stock-details",
    ),
    path(
        "admin/stocks/summary",
        admin.get_stocks_summary,
        name="api-v4-admin-get-stock-summary",
    ),
    path(
        "admin/stocks/filters",
        admin.get_stock_filters,
        name="api-v4-admin-get-stock-filters",
    ),
    # AUDITOR
    path("auditor/years", auditor.get_years, name="api-v4-auditor-get-years"),
    path("auditor/snapshot", auditor.get_snapshot, name="api-v4-auditor-get-snapshot"),
    path("auditor/lots", auditor.get_lots, name="api-v4-auditor-get-lots"),
    path(
        "auditor/lots/summary",
        auditor.get_lots_summary,
        name="api-v4-auditor-get-lots-summary",
    ),
    path(
        "auditor/lots/details",
        auditor.get_lot_details,
        name="api-v4-auditor-get-lot-details",
    ),
    path(
        "auditor/lots/filters",
        auditor.get_lots_filters,
        name="api-v4-auditor-get-lots-filters",
    ),
    path(
        "auditor/lots/toggle-warning",
        auditor.toggle_warning,
        name="api-v4-auditor-toggle-warning",
    ),
    path("auditor/lots/pin", auditor.toggle_pin, name="api-v4-auditor-pin-lots"),
    path("auditor/lots/comment", auditor.add_comment, name="api-v4-auditor-add-comment"),
    path("auditor/stocks", auditor.get_stocks, name="api-v4-auditor-get-stocks"),
    path(
        "auditor/stocks/details",
        auditor.get_stock_details,
        name="api-v4-auditor-get-stock-details",
    ),
    path(
        "auditor/stocks/summary",
        auditor.get_stocks_summary,
        name="api-v4-auditor-get-stock-summary",
    ),
    path(
        "auditor/stocks/filters",
        auditor.get_stock_filters,
        name="api-v4-auditor-get-stock-filters",
    ),
    path(
        "auditor/lots/mark-as-conform",
        auditor.mark_conform,
        name="api-v4-auditor-mark-as-conform",
    ),
    path(
        "auditor/lots/mark-as-nonconform",
        auditor.mark_nonconform,
        name="api-v4-auditor-mark-as-nonconform",
    ),
]

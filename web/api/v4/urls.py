from django.urls import path, include
from api.v4 import views

urlpatterns = [
    # GET
    path('years', views.get_years, name='api-v4-get-years'),
    path('snapshot', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots', views.get_lots, name='api-v4-get-lots'),
    path('lots/summary', views.get_lots_summary, name='api-v4-get-lots-summary'),
    path('lots/details', views.get_lot_details, name='api-v4-get-lot-details'),
    path('lots/filters', views.get_lots_filters, name='api-v4-get-lots-filters'),
    # POST
    ### Lot initial life
    path('lots/add', views.add_lot, name='api-v4-add-lots'),
    path('lots/add-excel', views.get_snapshot, name='api-v4-add-excel'),
    path('lots/duplicate', views.duplicate_lot, name='api-v4-duplicate-lot'),
    path('lots/update', views.update_lot, name='api-v4-update-lot'),
    path('lots/send', views.lots_send, name='api-v4-send-lots'),
    path('lots/delete', views.lots_delete, name='api-v4-delete-lots'),
    ### Corrections
    path('lots/comment', views.add_comment, name='api-v4-comment-lots'),
    path('lots/request-fix', views.request_fix, name='api-v4-request-fix'),
    path('lots/mark-as-fixed', views.mark_as_fixed, name='api-v4-mark-as-fixed'),
    path('lots/approve-fix', views.approve_fix, name='api-v4-approve-fix'),
    path('lots/reject', views.reject_lot, name='api-v4-reject-lots'),
    path('lots/recall', views.recall_lot, name='api-v4-recall-lot'),
    ### Approval
    path('lots/accept-release-for-consumption', views.accept_rfc, name='api-v4-accept-rfc'),
    path('lots/accept-in-stock', views.accept_in_stock, name='api-v4-accept-in-stock'),
    path('lots/accept-trading', views.accept_trading, name='api-v4-accept-trading'),
    path('lots/accept-processing', views.accept_processing, name='api-v4-accept-processing'),
    path('lots/accept-blending', views.accept_blending, name='api-v4-accept-blending'),
    path('lots/accept-export', views.accept_export, name='api-v4-accept-export'),

    # STOCKS
    path('stocks', views.get_stock, name='api-v4-get-stock'),
    path('stocks/summary', views.get_stocks_summary, name='api-v4-get-stock-summary'),
    path('stocks/details', views.get_stock_details, name='api-v4-get-stock-details'),
    path('stocks/cancel-transformation', views.stock_cancel_transformation, name='api-v4-cancel-transformation'),
    path('stocks/split', views.stock_split, name='api-v4-stock-split'),
    path('stocks/transform', views.stock_transform, name='api-v4-stock-transform'),
    path('stocks/flush', views.stock_flush, name='api-v4-stock-flush'),
    path('stocks/filters', views.get_stock_filters, name='api-v4-get-stock-filters'),

    # DECLARATIONS
    path('declarations', views.get_declarations, name='api-v4-get-declarations'),
    path('declarations/validate', views.validate_declaration, name='api-v4-validate-declaration'),
    path('declarations/invalidate', views.invalidate_declaration, name='api-v4-invalidate-declaration'),

    #### missing endpoints vs previous version
    # GET
    #path('declaration-summary', views.get_declaration_summary, name='api-v3-lots-get-declaration-summary'),
    #path('summary', views.get_lots_summary, name='api-v3-lots-get-lots-summary'),
    # POST
    # IMPORT/FILES
    #path('upload', views.upload, name='api-v3-upload'),
    #path('upload-blend', views.upload_blend, name='api-v3-upload-blend'),
    #path('download-template-simple', views.get_template_producers_simple, name='api-v3-template-simple'),
    #path('download-template-advanced', views.get_template_producers_advanced, name='api-v3-template-advanced'),
    #path('download-template-advanced-10k', views.get_template_producers_advanced_10k, name='api-v3-template-advanced-10k'),
    #path('download-template-blend', views.get_template_blend, name='api-v3-template-blend'),
    #path('download-template-trader', views.get_template_trader, name='api-v3-template-trader'),
]

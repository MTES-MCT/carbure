from django.urls import path, include
from api.v4 import views

urlpatterns = [
    # GET
    path('snapshot', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots', views.get_lots, name='api-v4-get-lots'),
    path('lots/details', views.get_details, name='api-v4-get-details'),
    # POST
    ### Lot initial life
    path('lots/add', views.get_snapshot, name='api-v4-add-lots'),
    path('lots/add-excel', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/update', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/send', views.get_snapshot, name='api-v4-get-snapshot'),
    ### Corrections
    path('lots/comment', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/request-fix', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/mark-as-fixed', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/approve-fix', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/reject', views.get_snapshot, name='api-v4-get-snapshot'),
    ### Approval
    path('lots/accept-release-for-consumption', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/accept-in-stock', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/accept-trading', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/accept-processing', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/accept-blending', views.get_snapshot, name='api-v4-get-snapshot'),
    path('lots/accept-export', views.get_snapshot, name='api-v4-get-snapshot'),


    # STOCKS
    path('stock', views.get_stock, name='api-v4-get-stock'),    
    path('stock/cancel-transformation', views.get_snapshot, name='api-v4-get-snapshot'),
    path('stock/split', views.get_snapshot, name='api-v4-get-snapshot'),
    path('stock/transform', views.get_snapshot, name='api-v4-get-snapshot'),
    path('stock/flush', views.get_snapshot, name='api-v4-get-snapshot'),

    # DECLARATIONS
    path('declarations/validate', views.get_snapshot, name='api-v4-get-snapshot'),
    path('declarations/invalidate', views.get_snapshot, name='api-v4-get-snapshot'),        
    #### missing endpoints vs previous version
    # GET
    #path('filters', views.get_filters, name='api-v3-lots-get-filters'),
    #path('declaration-summary', views.get_declaration_summary, name='api-v3-lots-get-declaration-summary'),
    #path('summary', views.get_lots_summary, name='api-v3-lots-get-lots-summary'),
    # POST
    #path('duplicate', views.duplicate_lot, name='api-v3-duplicate-lot'),
    # IMPORT/FILES
    #path('upload', views.upload, name='api-v3-upload'),
    #path('upload-blend', views.upload_blend, name='api-v3-upload-blend'),
    #path('download-template-simple', views.get_template_producers_simple, name='api-v3-template-simple'),
    #path('download-template-advanced', views.get_template_producers_advanced, name='api-v3-template-advanced'),
    #path('download-template-advanced-10k', views.get_template_producers_advanced_10k, name='api-v3-template-advanced-10k'),
    #path('download-template-blend', views.get_template_blend, name='api-v3-template-blend'),
    #path('download-template-trader', views.get_template_trader, name='api-v3-template-trader'),
]

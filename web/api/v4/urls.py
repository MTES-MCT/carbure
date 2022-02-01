from django.urls import path, include
from api.v4 import views, auth_views, certificates, admin

urlpatterns = [
    #### AUTH
    path('auth/register', auth_views.register, name='api-v4-register'),
    path('auth/login', auth_views.user_login, name='api-v4-login'),
    path('auth/logout', auth_views.user_logout, name='api-v4-logout'),
    path('auth/request-otp', auth_views.request_otp, name='api-v4-request-otp'),
    path('auth/verify-otp', auth_views.verify_otp, name='api-v4-verify-otp'),
    path('auth/request-password-reset', auth_views.request_password_reset, name='api-v4-request-password-reset'),
    path('auth/reset-password', auth_views.reset_password, name='api-v4-reset-password'),
    path('auth/request-activation-link', auth_views.request_activation_link, name='api-v4-request-activation-link'),
    path('auth/activate', auth_views.activate, name='api-v4-activate'),



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
    path('lots/add-excel', views.add_excel, name='api-v4-add-excel'),
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
    path('lots/accept-release-for-consumption', views.accept_rfc, name='api-v4-accept-rfc'), ### is this necessary? MAC are tagged when they are sent usually
    path('lots/accept-in-stock', views.accept_in_stock, name='api-v4-accept-in-stock'),
    path('lots/accept-trading', views.accept_trading, name='api-v4-accept-trading'),
    path('lots/accept-processing', views.accept_processing, name='api-v4-accept-processing'),
    path('lots/accept-blending', views.accept_blending, name='api-v4-accept-blending'),
    path('lots/accept-export', views.accept_export, name='api-v4-accept-export'),
    path('lots/accept-direct-delivery', views.accept_direct_delivery, name='api-v4-accept-direct-delivery'),
    ### Warnings
    path('lots/toggle-warning', views.toggle_warning, name='api-v4-toggle-warning'),

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
    path('download-template', views.get_template, name='api-v4-get-template'),
    path('download-template-stock', views.get_template_stock, name='api-v4-get-template-stock'),


    # SETTINGS
    path('get-certificates', certificates.get_certificates, name='api-v4-settings-get-certificates'),
    path('add-certificate', certificates.add_certificate, name='api-v4-settings-add-certificate'),
    path('delete-certificate', certificates.delete_certificate, name='api-v4-settings-delete-certificate'),
    path('update-certificate', certificates.update_certificate, name='api-v4-settings-update-certificate'),
    path('get-my-certificates', certificates.get_my_certificates, name='api-v4-settings-get-my-certificates'),
    path('set-production-site-certificates', certificates.set_production_site_certificates, name='api-v4-settings-set-production-site-certificates'),
    path('set-default-certificate', certificates.set_default_certificate, name='api-v4-settings-set-default-certificate'),


    # ADMIN
    path('admin/years', admin.get_years, name='api-v4-admin-get-years'),
    path('admin/snapshot', admin.get_snapshot, name='api-v4-admin-get-snapshot'),
    path('admin/lots', admin.get_lots, name='api-v4-admin-get-lots'),
    path('admin/lots/summary', admin.get_lots_summary, name='api-v4-admin-get-lots-summary'),
    path('admin/lots/details', admin.get_lot_details, name='api-v4-admin-get-lot-details'),
    path('admin/lots/filters', admin.get_lots_filters, name='api-v4-admin-get-lots-filters'),
    path('admin/lots/toggle-warning', admin.toggle_warning, name='api-v4-admin-toggle-warning'),
    path('admin/lots/pin', admin.toggle_pin, name='api-v4-admin-pin-lots'),
    path('admin/lots/comment', admin.add_comment, name='api-v4-admin-add-comment'),
]

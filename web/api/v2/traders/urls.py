from django.urls import path

from . import traders

urlpatterns = [
    path('upload-xlsx-template', traders.excel_template_upload, name='api-v2-traders-excel-template-upload'),
    path('download-xlsx-template', traders.excel_template_download, name='api-v2-traders-excel-template-download'),

    # get
    path('lots/drafts', traders.get_drafts, name='api-v2-traders-get-drafts'),
    path('lots/in', traders.get_in, name='api-v2-traders-get-in'),
    path('lots/out', traders.get_out, name='api-v2-traders-get-out'),

    # export
    path('lots/drafts/export', traders.export_drafts, name='api-v2-traders-export-drafts'),
    path('lots/in/export', traders.export_in, name='api-v2-traders-export-in'),
    path('lots/out/export', traders.export_out, name='api-v2-traders-export-out'),

    # post
    path('lots/delete', traders.delete_lots, name='api-v2-traders-delete-lots'),
    path('lots/accept', traders.accept_lots, name='api-v2-traders-accept-lots'),
    path('lots/declare', traders.declare_lots, name='api-v2-traders-declare-lots'),
    path('lots/validate', traders.validate_lots, name='api-v2-traders-validate-lots'),


    path('lot/reject', traders.reject_lot, name='api-v2-traders-reject-lot'),
    path('lot/accept', traders.accept_lot, name='api-v2-traders-accept-lot'),
    path('lot/accept-with-correction', traders.accept_lot_with_correction, name='api-v2-traders-accept-lot-with-correction'),
]

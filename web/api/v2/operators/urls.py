from django.urls import path

from . import operators

urlpatterns = [
    path('upload-xlsx-template', operators.excel_template_upload, name='api-v2-operators-excel-template-upload'),
    path('download-xlsx-template', operators.excel_template_download, name='api-v2-operators-excel-template-download'),

    # get
    path('lots/drafts', operators.get_drafts, name='api-v2-operators-get-drafts'),
    path('lots/in', operators.get_in, name='api-v2-operators-get-in'),
    path('lots/out', operators.get_out, name='api-v2-operators-get-out'),

    # export
    path('lots/drafts/export', operators.export_drafts, name='api-v2-operators-export-drafts'),
    path('lots/in/export', operators.export_in, name='api-v2-operators-export-in'),
    path('lots/out/export', operators.export_out, name='api-v2-operators-export-out'),

    # post
    path('lot/delete', operators.delete_lots, name='api-v2-operators-delete-lots'),
    path('lot/validate', operators.validate_lots, name='api-v2-operators-validate-lots'),
    path('lot/duplicate', operators.duplicate_lots, name='api-v2-operators-duplicate-lot'),
    path('lot/save', operators.save_lot, name='api-v2-operators-save-lot'),
    path('lot/reject', operators.reject_lot, name='api-v2-operators-reject-lot'),
    path('lot/accept', operators.accept_lot, name='api-v2-operators-accept-lot'),
    path('lots/accept', operators.accept_lots, name='api-v2-operators-accept-lots'),

    path('lot/accept-with-correction', operators.accept_lot_with_correction, name='api-v2-operators-accept-lot-with-correction'),
    path('lot/add-corrections', operators.add_lot_correction, name='api-v2-operators-add-lot-correction'),

]

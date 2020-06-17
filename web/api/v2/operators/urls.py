from django.urls import path

from . import operators

urlpatterns = [
    path('upload-xlsx-template', operators.excel_template_upload, name='api-v2-operators-excel-template-upload'),
    path('download-xlsx-template', operators.excel_template_download, name='api-v2-operators-excel-template-download'),

    # get
    path('lots/in', operators.get_in, name='api-v2-operators-get-in'),
    path('lots/mb', operators.get_mb, name='api-v2-operators-get-mb'),
    path('lots/out', operators.get_out, name='api-v2-operators-get-out'),

    # post
    path('lots/delete', operators.delete_lots, name='api-v2-operators_api-delete-lots'),
    path('lots/accept', operators.accept_lots, name='api-v2-operators_api-accept-lots'),
    path('lots/declare', operators.declare_lots, name='api-v2-operators_api-validate-lots'),


    path('lot/reject', operators.reject_lot, name='api-v2-operators-reject-lot'),
    path('lot/accept', operators.accept_lot, name='api-v2-operators-accept-lot'),
    path('lot/accept-with-correction', operators.accept_lot_with_correction, name='api-v2-operators-accept-lot-with-correction'),
]

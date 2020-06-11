from django.urls import path

from . import operators

urlpatterns = [
    path('upload-xlsx-template', operators.excel_template_upload, name='api-v2-operators-excel-template-upload'),
    path('download-xlsx-template-simple', operators.excel_template_download_simple, name='api-v2-operators-excel-template-download-simple'),
    path('download-xlsx-template-advanced', operators.excel_template_download_advanced, name='api-v2-operators-excel-template-download-advanced'),

    # get
    path('lots/drafts', operators.get_drafts, name='api-v2-operators-get-drafts'),
    path('lots/received', operators.get_received, name='api-v2-operators-get-received'),
    path('lots/declared', operators.get_declared, name='api-v2-operators-get-declared'),

    # post
    path('lots/delete', operators.delete_lots, name='api-v2-operators_api-delete-lots'),
    path('lots/accept', operators.accept_lots, name='api-v2-operators_api-accept-lots'),
    path('lots/declare', operators.declare_lots, name='api-v2-operators_api-validate-lots'),
]

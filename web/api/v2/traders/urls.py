from django.urls import path

from . import traders_get
from . import traders_post
from . import traders_files

urlpatterns = [
    # files / templates
    path('upload-mb-xlsx-template', traders_files.excel_mb_template_upload, name='api-v2-traders-excel-mb-template-upload'),
    path('upload-xlsx-template', traders_files.excel_template_upload, name='api-v2-traders-excel-template-upload'),
    path('download-xlsx-template', traders_files.excel_template_download, name='api-v2-traders-excel-template-download'),
    path('download-xlsx-template-mb', traders_files.excel_template_download_mb, name='api-v2-traders-excel-template-mb'),
    path('lots/drafts/export', traders_files.export_drafts, name='api-v2-traders-export-drafts'),
    path('lots/in/export', traders_files.export_in, name='api-v2-traders-export-in'),
    path('lots/out/export', traders_files.export_out, name='api-v2-traders-export-out'),
    path('lots/mb/export', traders_files.export_mb, name='api-v2-traders-export-mb'),


    # GET
    path('lots/drafts', traders_get.get_drafts, name='api-v2-traders-get-drafts'),
    path('lots/mb-drafts', traders_get.get_mb_drafts, name='api-v2-traders-get-mb-drafts'),
    path('lots/in', traders_get.get_in, name='api-v2-traders-get-in'),
    path('lots/mb', traders_get.get_mb, name='api-v2-traders-get-mb'),
    path('lots/corrections', traders_get.get_corrections, name='api-v2-traders-get-corrections'),
    path('lots/out', traders_get.get_out, name='api-v2-traders-get-out'),


    # POST
    path('lot/delete', traders_post.delete_lots, name='api-v2-traders-delete-lots'),
    path('lot/validate', traders_post.validate_lots, name='api-v2-traders-validate-lots'),
    path('lot/duplicate', traders_post.duplicate_lot, name='api-v2-traders-duplicate-lot'),
    path('lot/save', traders_post.save_lot, name='api-v2-traders-save-lot'),
    path('lot/reject', traders_post.reject_lot, name='api-v2-traders-reject-lot'),
    path('lot/accept', traders_post.accept_lot, name='api-v2-traders-accept-lot'),
    path('lots/accept', traders_post.accept_lots, name='api-v2-traders-accept-lots'),
    path('lot/accept-with-correction', traders_post.accept_lot_with_correction, name='api-v2-traders-accept-lot-with-correction'),
    path('lot/add-corrections', traders_post.add_lot_correction, name='api-v2-traders-add-lot-correction'),
    path('lot/mb/delete-drafts', traders_post.delete_mb_drafts_lots, name='api-v2-traders-delete-mb-drafts'),
    path('lot/mb/validate-drafts', traders_post.validate_mb_drafts_lots, name='api-v2-traders-validate-mb-drafts-lots'),
    path('lot/mb/fuse', traders_post.fuse_mb_lots, name='api-v2-traders-fuse-mb-lots'),
]

from django.urls import path
from . import views

urlpatterns = [
    # GET
    #path('lots/drafts', views.get_drafts, name='api-v2-producers-get-drafts'),
    #path('lots/mb-drafts', views.get_mb_drafts, name='api-v2-producers-get-mb-drafts'),
    #path('lots/in', views.get_in, name='api-v2-producers-get-in'),
    #path('lots/mb', views.get_mb, name='api-v2-producers-get-mb'),
    #path('lots/corrections', views.get_corrections, name='api-v2-producers-get-corrections'),
    #path('lots/out', views.get_out, name='api-v2-producers-get-out'),


    # POST
    #path('lot/delete', views.delete_lots, name='api-v2-producers-delete-lots'),
    #path('lot/delete-all-drafts', views.delete_all_drafts, name='api-v2-producers-delete-all-drafts'),
    #path('lot/validate', views.validate_lots, name='api-v2-producers-validate-lots'),
    #path('lot/duplicate', views.duplicate_lot, name='api-v2-producers-duplicate-lot'),
    #path('lot/save', views.save_lot, name='api-v2-producers-save-lot'),
    #path('lot/reject', views.reject_lot, name='api-v2-producers-reject-lot'),
    #path('lot/accept', views.accept_lot, name='api-v2-producers-accept-lot'),
    #path('lots/accept', views.accept_lots, name='api-v2-producers-accept-lots'),
    #path('lot/accept-with-correction', views.accept_lot_with_correction, name='api-v2-producers-accept-lot-with-correction'),
    #path('lot/add-corrections', views.add_lot_correction, name='api-v2-producers-add-lot-correction'),
    #path('lot/mb/delete-drafts', views.delete_mb_drafts_lots, name='api-v2-producers-delete-mb-drafts'),
    #path('lot/mb/validate-drafts', views.validate_mb_drafts_lots, name='api-v2-producers-validate-mb-drafts-lots'),
    #path('lot/mb/fuse', views.fuse_mb_lots, name='api-v2-producers-fuse-mb-lots'),

    # files
    #path('upload-xlsx-template', views.excel_template_upload, name='api-v2-producers-excel-template-upload'),
    #path('upload-mb-xlsx-template', views.excel_mb_template_upload, name='api-v2-producers-excel-mb-template-upload'),
    #path('download-xlsx-template-simple', views.excel_template_download_simple, name='api-v2-producers-excel-template-download-simple'),
    #path('download-xlsx-template-advanced', views.excel_template_download_advanced, name='api-v2-producers-excel-template-download-advanced'),
    #path('download-xlsx-template-mb', views.excel_template_download_mb, name='api-v2-producers-excel-template-mb'),
    #path('export/lots/drafts', views.export_drafts, name='api-v2-producers-export-drafts'),
    #path('export/lots/mb', views.export_mb, name='api-v2-producers-export-mb'),
    #path('export/lots/histo', views.export_histo, name='api-v2-producers-export-histo'),


]

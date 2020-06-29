from django.urls import path

from . import producers_get
from . import producers_post
from . import producers_files
from . import producers_misc


urlpatterns = [
    # files
    path('upload-xlsx-template', producers_files.excel_template_upload, name='api-v2-producers-excel-template-upload'),
    path('upload-mb-xlsx-template', producers_files.excel_mb_template_upload, name='api-v2-producers-excel-mb-template-upload'),
    path('download-xlsx-template-simple', producers_files.excel_template_download_simple, name='api-v2-producers-excel-template-download-simple'),
    path('download-xlsx-template-advanced', producers_files.excel_template_download_advanced, name='api-v2-producers-excel-template-download-advanced'),
    path('download-xlsx-template-mb', producers_files.excel_template_download_mb, name='api-v2-producers-excel-template-mb'),
    path('export/lots/drafts', producers_files.export_drafts, name='api-v2-producers-export-drafts'),
    path('export/lots/mb', producers_files.export_mb, name='api-v2-producers-export-mb'),

    # GET
    path('lots/drafts', producers_get.get_drafts, name='api-v2-producers-get-drafts'),
    path('lots/mb-drafts', producers_get.get_mb_drafts, name='api-v2-producers-get-mb-drafts'),
    path('lots/in', producers_get.get_in, name='api-v2-producers-get-in'),
    path('lots/mb', producers_get.get_mb, name='api-v2-producers-get-mb'),
    path('lots/corrections', producers_get.get_corrections, name='api-v2-producers-get-corrections'),
    path('lots/out', producers_get.get_out, name='api-v2-producers-get-out'),


    # POST
    path('lot/delete', producers_post.delete_lots, name='api-v2-producers-delete-lots'),
    path('lot/validate', producers_post.validate_lots, name='api-v2-producers-validate-lots'),
    path('lot/duplicate', producers_post.duplicate_lot, name='api-v2-producers-duplicate-lot'),
    path('lot/save', producers_post.save_lot, name='api-v2-producers-save-lot'),
    path('lot/reject', producers_post.reject_lot, name='api-v2-producers-reject-lot'),
    path('lot/accept', producers_post.accept_lot, name='api-v2-producers-accept-lot'),
    path('lots/accept', producers_post.accept_lots, name='api-v2-producers-accept-lots'),
    path('lot/accept-with-correction', producers_post.accept_lot_with_correction, name='api-v2-producers-accept-lot-with-correction'),
    path('lot/add-corrections', producers_post.add_lot_correction, name='api-v2-producers-add-lot-correction'),
    path('lot/mb/delete-drafts', producers_post.delete_mb_drafts_lots, name='api-v2-producers-delete-mb-drafts'),
    path('lot/mb/validate-drafts', producers_post.validate_mb_drafts_lots, name='api-v2-producers-validate-mb-drafts-lots'),
    path('lot/mb/fuse', producers_post.fuse_mb_lots, name='api-v2-producers-fuse-mb-lots'),


    # misc
    path('get-producers-autocomplete', producers_misc.get_producers_autocomplete, name='api-v2-producers-autocomplete'),
    path('get-clients-autocomplete', producers_misc.get_clients_autocomplete, name='api-v2-clients-autocomplete'),
    path('get-depots-autocomplete', producers_misc.get_depots_autocomplete, name='api-v2-depots-autocomplete'),
    path('get-prodsites-autocomplete', producers_misc.get_prod_site_autocomplete, name='api-v2-production-sites-autocomplete'),
    path('get-mps-autocomplete', producers_misc.get_mps_autocomplete, name='api-v2-mps-autocomplete'),
    path('get-bcs-autocomplete', producers_misc.get_biocarburants_autocomplete, name='api-v2-biocarburants-autocomplete'),

    path('get-ges', producers_misc.get_ges, name='api-v2-get-ges'),

]

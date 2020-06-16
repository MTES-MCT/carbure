from django.urls import path

from . import producers

urlpatterns = [
    # private, producers
    path('upload-xlsx-template', producers.excel_template_upload, name='api-v2-producers-excel-template-upload'),
    path('download-xlsx-template-simple', producers.excel_template_download_simple, name='api-v2-producers-excel-template-download-simple'),
    path('download-xlsx-template-advanced', producers.excel_template_download_advanced, name='api-v2-producers-excel-template-download-advanced'),


    path('lots/drafts', producers.get_drafts, name='api-v2-producers-get-drafts'),
    path('lots/received', producers.get_received, name='api-v2-producers-get-received'),
    path('lots/mb', producers.get_mb, name='api-v2-producers-get-mb'),
    path('lots/corrections', producers.get_corrections, name='api-v2-producers-get-corrections'),
    path('lots/valid', producers.get_valid, name='api-v2-producers-get-valid'),

    path('export/lots/drafts', producers.export_drafts, name='api-v2-producers-export-drafts'),
    path('export/lots/mb', producers.export_mb, name='api-v2-producers-export-mb'),



    path('producers/lot/delete', producers.delete_lots, name='api-v2-producers-delete-lots'),
    path('producers/lot/validate', producers.validate_lots, name='api-v2-producers-validate-lots'),
    path('producers/lot/duplicate', producers.duplicate_lot, name='api-v2-producers-duplicate-lot'),
    path('producers/lot/save', producers.save_lot, name='api-v2-producers-save-lot'),
    path('producers/lot/reject', producers.reject_lot, name='api-v2-producers-reject-lot'),
    path('producers/lot/accept', producers.accept_lot, name='api-v2-producers-accept-lot'),
    path('producers/lot/accept-with-correction', producers.accept_lot_with_correction, name='api-v2-producers-accept-lot-with-correction'),
    path('producers/lots/accept', producers.accept_lots, name='api-v2-producers-accept-lots'),


    path('producers/get-producers-autocomplete', producers.get_producers_autocomplete, name='api-v2-producers-autocomplete'),
    path('producers/get-clients-autocomplete', producers.get_clients_autocomplete, name='api-v2-clients-autocomplete'),
    path('producers/get-depots-autocomplete', producers.get_depots_autocomplete, name='api-v2-depots-autocomplete'),
]

#path('producers/lots/corrections', producers_api.producers_lots_corrections, name='api-producers-lots-corrections'),
#path('producers/lots/valid', producers_api.producers_lots_valid, name='api-producers-lots-valid'),
#path('producers/lots/all', producers_api.producers_lots_all, name='api-producers-lots-all'),

#path('producers/lot/save', producers_api.producers_save_lot, name='producers-api-attestation-save-lot'),

#path('producers/lot/comments', producers_api.producers_lot_comments, name='producers-api-lot-comments'),
#path('producers/lot/save-comment', producers_api.producers_lot_save_comment, name='producers-api-save-comment'),
#path('producers/lot/errors', producers_api.producers_lot_errors, name='producers-api-lot-errors'),

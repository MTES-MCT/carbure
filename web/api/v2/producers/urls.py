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



    path('lot/delete', producers.delete_lots, name='api-v2-producers-delete-lots'),
    path('lot/validate', producers.validate_lots, name='api-v2-producers-validate-lots'),
    path('lot/duplicate', producers.duplicate_lot, name='api-v2-producers-duplicate-lot'),
    path('lot/save', producers.save_lot, name='api-v2-producers-save-lot'),
    path('lot/reject', producers.reject_lot, name='api-v2-producers-reject-lot'),
    path('lot/accept', producers.accept_lot, name='api-v2-producers-accept-lot'),
    path('lot/accept-with-correction', producers.accept_lot_with_correction, name='api-v2-producers-accept-lot-with-correction'),
    path('lot/get-corrections', producers.get_lot_corrections, name='api-v2-producers-get-lot-corrections'),
    path('lot/add-corrections', producers.add_lot_correction, name='api-v2-producers-add-lot-correction'),

    path('producers/lots/accept', producers.accept_lots, name='api-v2-producers-accept-lots'),


    path('producers/get-producers-autocomplete', producers.get_producers_autocomplete, name='api-v2-producers-autocomplete'),
    path('producers/get-clients-autocomplete', producers.get_clients_autocomplete, name='api-v2-clients-autocomplete'),
    path('producers/get-depots-autocomplete', producers.get_depots_autocomplete, name='api-v2-depots-autocomplete'),
]

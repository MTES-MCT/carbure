from django.urls import path

from . import producers

urlpatterns = [
    # private, producers
    path('upload-xlsx-template', producers.excel_template_upload, name='api-v2-producers-excel-template-upload'),
    path('download-xlsx-template-simple', producers.excel_template_download_simple, name='api-v2-producers-excel-template-download-simple'),
    path('download-xlsx-template-advanced', producers.excel_template_download_advanced, name='api-v2-producers-excel-template-download-advanced'),
    path('lots/drafts', producers.get_drafts, name='api-v2-producers-get-drafts'),
    path('lots/received', producers.get_received, name='api-v2-producers-get-received'),
    path('lots/corrections', producers.get_corrections, name='api-v2-producers-get-corrections'),
    path('lots/valid', producers.get_valid, name='api-v2-producers-get-valid'),

    path('producers/lot/delete', producers.delete_lots, name='api-v2-producers-delete-lots'),
    path('producers/lot/validate', producers.validate_lots, name='api-v2-producers-validate-lots'),
    path('producers/lot/duplicate', producers.duplicate_lot, name='api-v2-producers-duplicate-lot'),
    path('producers/lot/save', producers.save_lot, name='api-v2-producers-save-lot'),
]

#path('producers/lots/corrections', producers_api.producers_lots_corrections, name='api-producers-lots-corrections'),
#path('producers/lots/valid', producers_api.producers_lots_valid, name='api-producers-lots-valid'),
#path('producers/lots/all', producers_api.producers_lots_all, name='api-producers-lots-all'),

#path('producers/lot/save', producers_api.producers_save_lot, name='producers-api-attestation-save-lot'),

#path('producers/lot/comments', producers_api.producers_lot_comments, name='producers-api-lot-comments'),
#path('producers/lot/save-comment', producers_api.producers_lot_save_comment, name='producers-api-save-comment'),
#path('producers/lot/errors', producers_api.producers_lot_errors, name='producers-api-lot-errors'),

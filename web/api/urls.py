from django.urls import path, include

from . import public_api
from . import producers_api
from . import operators_api
from . import administrators_api

urlpatterns = [
    path('v2/producers/', include('api.v2.producers.urls')),

    # public, autocomplete api
    path('biocarburant-autocomplete/', public_api.biocarburant_autocomplete, name='api-biocarburant-autocomplete'),
    path('matiere-premiere-autocomplete/', public_api.matiere_premiere_autocomplete, name='api-matiere-premiere-autocomplete'),
    path('country-autocomplete/', public_api.country_autocomplete, name='api-country-autocomplete'),
    path('operators-autocomplete/', public_api.operators_autocomplete, name='api-operators-autocomplete'),
    path('depots-autocomplete/', public_api.depots_autocomplete, name='api-depots-autocomplete'),

    path('biocarburant-csv/', public_api.biocarburant_csv, name='api-biocarburant-csv'),
    path('matiere-premiere-csv/', public_api.matiere_premiere_csv, name='api-matiere-premiere-csv'),
    path('country-csv/', public_api.country_csv, name='api-country-csv'),
    path('operators-csv/', public_api.operators_csv, name='api-operators-csv'),
    path('depots-csv/', public_api.depots_csv, name='api-depots-csv'),

    # private, producers
    path('producers/csv-template', producers_api.producers_import_csv_template, name='api-producers-template-csv'),
    path('producers/csv/upload', producers_api.producers_upload_csv, name='producers-api-upload-csv'),
    path('producers/xlsx-template', producers_api.producers_import_excel_template, name='api-producers-template-excel'),
    path('producers/lots/drafts', producers_api.producers_lots_drafts, name='api-producers-lots-drafts'),
    path('producers/lots/corrections', producers_api.producers_lots_corrections, name='api-producers-lots-corrections'),
    path('producers/lots/valid', producers_api.producers_lots_valid, name='api-producers-lots-valid'),
    path('producers/lots/all', producers_api.producers_lots_all, name='api-producers-lots-all'),
    path('producers/lot/save', producers_api.producers_save_lot, name='producers-api-attestation-save-lot'),
    path('producers/lot/duplicate', producers_api.producers_duplicate_lot, name='producers-api-duplicate-lot'),
    path('producers/lot/delete', producers_api.producers_delete_lots, name='producers-api-delete-lots'),
    path('producers/lot/validate', producers_api.producers_validate_lots, name='producers-api-validate-lots'),
    path('producers/lot/comments', producers_api.producers_lot_comments, name='producers-api-lot-comments'),
    path('producers/lot/save-comment', producers_api.producers_lot_save_comment, name='producers-api-save-comment'),
    path('producers/lot/errors', producers_api.producers_lot_errors, name='producers-api-lot-errors'),
    path('producers/settings/add-site', producers_api.producers_settings_add_site, name='producers-api-settings-add-site'),
    path('producers/settings/add-certif', producers_api.producers_settings_add_certif, name='producers-api-settings-add-certif'),
    path('producers/settings/delete-certif', producers_api.producers_settings_delete_certif, name='producers-api-settings-delete-certif'),
    path('producers/settings/add-mp', producers_api.producers_settings_add_mp, name='producers-api-settings-add-mp'),
    path('producers/settings/add-biocarburant', producers_api.producers_settings_add_biocarburant, name='producers-api-settings-add-biocarburant'),
    path('producers/settings/delete-mp', producers_api.producers_settings_delete_mp, name='producers-api-settings-delete-mp'),
    path('producers/settings/delete-biocarburant', producers_api.producers_settings_delete_biocarburant, name='producers-api-settings-delete-bc'),
    path('producers/export/drafts', producers_api.producers_attestation_export_drafts, name='producers-api-attestation-export-drafts'),
    path('producers/export/valid', producers_api.producers_attestation_export_valid, name='producers-api-attestation-export-valid'),
    path('producers/corrections', producers_api.producers_corrections, name='api-producers-corrections'),
    path('producers/production-sites-autocomplete/', producers_api.producers_prod_site_autocomplete, name='producers-api-production-sites-autocomplete'),
    path('producers/biocarburant-autocomplete/', producers_api.producers_biocarburant_autocomplete, name='producers-api-biocarburants-autocomplete'),
    path('producers/mp-autocomplete/', producers_api.producers_mp_autocomplete, name='producers-api-mps-autocomplete'),
    path('producers/ges/', producers_api.producers_ges, name='producers-api-ges'),

    # private, operators
    path('operators/lots/declared', operators_api.operators_lots, name='operators-api-declared-lots'),
    path('operators/lots/affiliated', operators_api.operators_lots_affilies, name='operators-api-affiliated-lots'),
    path('operators/lots/accept', operators_api.operators_lot_accept, name='operators-api-accept-lots'),
    path('operators/lots/accept-correction', operators_api.operators_lot_accept_correction, name='operators-api-accept-lot-correction'),
    path('operators/lots/accept-with-comment', operators_api.operators_lot_accept_with_comment, name='operators-api-accept-lot-with-comment'),
    path('operators/lots/reject', operators_api.operators_lot_reject, name='operators-api-reject-lots'),
    path('operators/lots/comments', operators_api.operators_lot_comments, name='operators-api-lot-comments'),
    path('operators/lots/export', operators_api.operators_export_lots, name='operators-api-declaration-export'),
    path('operators/lots/affiliated/export', operators_api.operators_export_affiliated, name='operators-api-export-affiliated'),

    # private, administrators
    path('administrators/users-autocomplete/', administrators_api.admin_users_autocomplete, name='admin-api-users-autocomplete'),
    path('administrators/entities-autocomplete/', administrators_api.admin_entities_autocomplete, name='admin-api-entities-autocomplete'),
    path('administrators/lots', administrators_api.admin_lots, name='admin-api-lots'),
    path('administrators/export', administrators_api.admin_lots_export, name='admin-api-lots-export'),

]

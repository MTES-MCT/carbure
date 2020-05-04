from django.urls import path

from . import views

urlpatterns = [
	# public, autocomplete api
	path('biocarburant-autocomplete/', views.biocarburant_autocomplete, name='api-biocarburant-autocomplete'),
	path('matiere-premiere-autocomplete/', views.matiere_premiere_autocomplete, name='api-matiere-premiere-autocomplete'),
    path('country-autocomplete/', views.country_autocomplete, name='api-country-autocomplete'),
	path('operators-autocomplete/', views.operators_autocomplete, name='api-operators-autocomplete'),

    # public csv
    path('biocarburant-csv/', views.biocarburant_csv, name='api-biocarburant-csv'),
    path('matiere-premiere-csv/', views.matiere_premiere_csv, name='api-matiere-premiere-csv'),
    path('country-csv/', views.country_csv, name='api-country-csv'),
    path('operators-csv/', views.operators_csv, name='api-operators-csv'),

    # private template
    path('producers-template-csv/', views.producers_import_csv_template, name='api-producers-template-csv'),

    # private, producers
    path('producers/lots/<int:attestation_id>', views.producers_lots, name='api-producers-lots'),
    path('producers/lots', views.producers_all_lots, name='api-producers-all-lots'),
    path('producers/corrections', views.producers_corrections, name='api-producers-corrections'),
    path('producers/production-sites-autocomplete/', views.producers_prod_site_autocomplete, name='producers-api-production-sites-autocomplete'),
    path('producers/biocarburant-autocomplete/', views.producers_biocarburant_autocomplete, name='producers-api-biocarburants-autocomplete'),
    path('producers/mp-autocomplete/', views.producers_mp_autocomplete, name='producers-api-mps-autocomplete'),
    path('producers/ges/', views.producers_ges, name='producers-api-ges'),
    path('producers/settings/add-site', views.producers_settings_add_site, name='producers-api-settings-add-site'),
    path('producers/settings/add-certif', views.producers_settings_add_certif, name='producers-api-settings-add-certif'),
    path('producers/settings/delete-certif', views.producers_settings_delete_certif, name='producers-api-settings-delete-certif'),
    path('producers/settings/add-mp', views.producers_settings_add_mp, name='producers-api-settings-add-mp'),
    path('producers/settings/add-biocarburant', views.producers_settings_add_biocarburant, name='producers-api-settings-add-biocarburant'),
    path('producers/settings/delete-mp', views.producers_settings_delete_mp, name='producers-api-settings-delete-mp'),
    path('producers/settings/delete-biocarburant', views.producers_settings_delete_biocarburant, name='producers-api-settings-delete-bc'),
    path('producers/lot/save', views.producers_save_lot, name='producers-api-attestation-save-lot'),
    path('producers/lot/duplicate', views.producers_duplicate_lot, name='producers-api-duplicate-lot'),
    path('producers/lot/delete', views.producers_delete_lots, name='producers-api-delete-lots'),
    path('producers/lot/validate', views.producers_validate_lots, name='producers-api-validate-lots'),
    path('producers/lot/comments', views.producers_lot_comments, name='producers-api-lot-comments'),
    path('producers/attestation/<int:attestation_id>/export', views.producers_attestation_export, name='producers-api-attestation-export'),
    path('producers/lot/save-comment', views.producers_lot_save_comment, name='producers-api-save-comment'),
    path('producers/lot/errors', views.producers_lot_errors, name='producers-api-lot-errors'),

    # private, operators
    path('operators/lots-affilies', views.operators_lots_affilies, name='operators-api-affiliated-lots'),
    path('operators/lots/accept', views.operators_lot_accept, name='operators-api-accept-lots'),
    path('operators/lots/accept-correction', views.operators_lot_accept_correction, name='operators-api-accept-lot-correction'),
    path('operators/lots/accept-with-comment', views.operators_lot_accept_with_comment, name='operators-api-accept-lot-with-comment'),
    path('operators/lots/reject', views.operators_lot_reject, name='operators-api-reject-lots'),
    path('operators/lots/<int:declaration_id>', views.operators_lots, name='operators-api-lots'),
    path('operators/lot/comments', views.operators_lot_comments, name='operators-api-lot-comments'),
    path('operators/settings/add-depot', views.operators_settings_add_depot, name='operators-api-settings-add-depot'),
    path('operators/declaration/<int:declaration_id>/export', views.operators_declaration_export, name='operators-api-declaration-export'),



    # private, administrators
    path('administrators/users-autocomplete/', views.admin_users_autocomplete, name='admin-api-users-autocomplete'),
    path('administrators/entities-autocomplete/', views.admin_entities_autocomplete, name='admin-api-entities-autocomplete'),
    path('administrators/lots', views.admin_lots, name='admin-api-lots'),
    path('administrators/export', views.admin_lots_export, name='admin-api-lots-export'),

]

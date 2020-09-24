from api.v1 import public_api, producers_api, administrators_api
from django.urls import path


urlpatterns = [
    # ALL BELOW CALLS ARE DEPRECATED
    # api v1
    path('producers/add-production-site', producers_api.producers_settings_add_site,
         name='producers-api-settings-add-site'),
    path('producers/add-production-site-certificate', producers_api.producers_settings_add_certif,
         name='producers-api-settings-add-certif'),
    path('producers/delete-production-site-certificate', producers_api.producers_settings_delete_certif,
         name='producers-api-settings-delete-certif'),
    path('producers/delete-production-site-mp', producers_api.producers_settings_delete_mp,
         name='producers-api-settings-delete-mp'),
    path('producers/add-production-site-mp', producers_api.producers_settings_add_mp,
         name='producers-api-settings-add-mp'),
    path('producers/delete-production-site-bc', producers_api.producers_settings_delete_biocarburant,
         name='producers-api-settings-delete-bc'),
    path('producers/add-production-site-bc', producers_api.producers_settings_add_biocarburant,
         name='producers-api-settings-add-biocarburant'),

    # public, autocomplete api
    path('public/biocarburant-autocomplete/', public_api.biocarburant_autocomplete,
         name='api-biocarburant-autocomplete'),
    path('public/matiere-premiere-autocomplete/', public_api.matiere_premiere_autocomplete,
         name='api-matiere-premiere-autocomplete'),
    path('public/country-autocomplete/', public_api.country_autocomplete, name='api-country-autocomplete'),
    path('public/operators-autocomplete/', public_api.operators_autocomplete, name='api-operators-autocomplete'),
    path('public/depots-autocomplete/', public_api.depots_autocomplete, name='api-depots-autocomplete'),
    path('public/biocarburant-csv/', public_api.biocarburant_csv, name='api-biocarburant-csv'),
    path('public/matiere-premiere-csv/', public_api.matiere_premiere_csv, name='api-matiere-premiere-csv'),
    path('public/country-csv/', public_api.country_csv, name='api-country-csv'),
    path('public/operators-csv/', public_api.operators_csv, name='api-operators-csv'),
    path('public/depots-csv/', public_api.depots_csv, name='api-depots-csv'),

    # private, administrators
    path('administrators/users-autocomplete/', administrators_api.admin_users_autocomplete,
         name='admin-api-users-autocomplete'),
    path('administrators/entities-autocomplete/', administrators_api.admin_entities_autocomplete,
         name='admin-api-entities-autocomplete'),
]

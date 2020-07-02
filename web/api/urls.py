from django.urls import path, include

from . import public_api
from . import producers_api
from . import administrators_api

urlpatterns = [
    path('v2/producers/', include('api.v2.producers.urls')),
    path('v2/operators/', include('api.v2.operators.urls')),
    path('v2/traders/', include('api.v2.traders.urls')),


    # api v1
    path('v1/producers/add-production-site', producers_api.producers_settings_add_site, name='producers-api-settings-add-site'),
    path('v1/producers/add-production-site-certificate', producers_api.producers_settings_add_certif, name='producers-api-settings-add-certif'),
    path('v1/producers/delete-production-site-certificate', producers_api.producers_settings_delete_certif, name='producers-api-settings-delete-certif'),
    path('v1/producers/delete-production-site-mp', producers_api.producers_settings_delete_mp, name='producers-api-settings-delete-mp'),
    path('v1/producers/add-production-site-mp', producers_api.producers_settings_add_mp, name='producers-api-settings-add-mp'),
    path('v1/producers/delete-production-site-bc', producers_api.producers_settings_delete_biocarburant, name='producers-api-settings-delete-bc'),
    path('v1/producers/add-production-site-bc', producers_api.producers_settings_add_biocarburant, name='producers-api-settings-add-biocarburant'),


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


    # private, administrators
    path('administrators/users-autocomplete/', administrators_api.admin_users_autocomplete, name='admin-api-users-autocomplete'),
    path('administrators/entities-autocomplete/', administrators_api.admin_entities_autocomplete, name='admin-api-entities-autocomplete'),
    path('administrators/lots', administrators_api.admin_lots, name='admin-api-lots'),
    path('administrators/export', administrators_api.admin_lots_export, name='admin-api-lots-export'),

]

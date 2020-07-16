from django.urls import path, include

from . import public_api
from . import producers_api
from . import administrators_api
from api.v2 import shared

urlpatterns = [
    path('v2/producers/', include('api.v2.producers.urls')),
    path('v2/operators/', include('api.v2.operators.urls')),
    path('v2/traders/', include('api.v2.traders.urls')),
    path('v2/administrators/', include('api.v2.administrators.urls')),


    # misc - automplete
    path('v2/shared/get-producers-autocomplete', shared.get_producers_autocomplete, name='api-v2-producers-autocomplete'),
    path('v2/shared/get-clients-autocomplete', shared.get_clients_autocomplete, name='api-v2-clients-autocomplete'),
    path('v2/shared/get-depots-autocomplete', shared.get_depots_autocomplete, name='api-v2-depots-autocomplete'),
    path('v2/shared/get-prodsites-autocomplete', shared.get_prod_site_autocomplete, name='api-v2-production-sites-autocomplete'),
    path('v2/shared/get-mps-autocomplete', shared.get_mps_autocomplete, name='api-v2-mps-autocomplete'),
    path('v2/shared/get-bcs-autocomplete', shared.get_biocarburants_autocomplete, name='api-v2-biocarburants-autocomplete'),
    path('v2/shared/get-ges', shared.get_ges, name='api-v2-get-ges'),



    # ALL BELOW CALLS NEED TO BE DEPRECATED:
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

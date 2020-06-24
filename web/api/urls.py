from django.urls import path, include

from . import public_api
from . import operators_api
from . import administrators_api

urlpatterns = [
    path('v2/producers/', include('api.v2.producers.urls')),
    path('v2/operators/', include('api.v2.operators.urls')),
    path('v2/traders/', include('api.v2.traders.urls')),



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

from django.urls import path
from . import views

urlpatterns = [
    path("users", views.get_users, name="api-v3-admin-get-users"),
    path("users/rights-requests", views.get_rights_requests, name="api-v3-admin-get-rights-requests"),
    path("users/update-right-request", views.update_right_request, name="api-v3-admin-update-right-request"),
    # path("entities", views.get_entities, name="api-v3-admin-get-entities"),
    # path("entities/details", views.get_entity_details, name="api-v3-admin-get-entity-details"),
    path("entities/add", views.add_entity, name="api-v3-admin-add-entity"),
    # path("entities/del", views.delete_entity, name="api-v3-admin-delete-entity"), #never used > je l'ai donc supprimé
    path("entities/depots", views.get_entity_depots, name="api-v3-admin-get-entity-depots"),  # TODO doenst works
    # path(
    #     "entities/production_sites", views.get_entity_production_sites, name="api-v3-admin-get-entity-production-sites"
    # ),
    path("entities/certificates", views.get_entity_certificates, name="api-v3-admin-get-entity-certificates"),
    # MAP VISUALIZATION
    path("map", views.map, name="api-v3-admin-map"),
]

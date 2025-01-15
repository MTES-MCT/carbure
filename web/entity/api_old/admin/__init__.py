from django.urls import path, include
from .entities import get_entities
from .details import get_entity_details
from .create import create_entity
from .depots import get_entity_depots
from .production_sites import get_entity_production_sites

urlpatterns = [
    path("certificates/", include("entity.api_old.admin.certificates")),
    path("users/", include("entity.api_old.admin.users")),
    path("", get_entities, name="transactions-admin-entities"),
    path("create", create_entity, name="transactions-admin-entities-create"),
    path("details", get_entity_details, name="transactions-admin-entities-details"),
    path("depots", get_entity_depots, name="transactions-admin-entities-depots"),
    path("production_sites", get_entity_production_sites, name="transactions-admin-entities-production-sites"),
]

from django.urls import path, include
from .entities import get_entities
from .details import get_entity_details
from .create import create_entity
from .depots import get_entity_depots
from .production_sites import get_entity_production_sites

urlpatterns = [
    path("certificates/", include("admin.api.entities.certificates")),
    path("users/", include("admin.api.entities.users")),
    path("", get_entities, name="admin-entities"),
    path("create", create_entity, name="admin-entities-create"),
    path("details", get_entity_details, name="admin-entities-details"),
    path("depots", get_entity_depots, name="admin-entities-depots"),
    path("production_sites", get_entity_production_sites, name="admin-entities-production-sites"),
]

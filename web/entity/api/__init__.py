from django.urls import path, include

from .update_info import update_entity_info
from .stats import get_entity_stats
from .search_company import search_company

urlpatterns = [
    path("depots/", include("entity.api.depots")),
    path("production-sites/", include("entity.api.production_sites")),
    path("users/", include("entity.api.users")),
    path("certificates/", include("entity.api.certificates")),
    path("options/", include("entity.api.options")),
    path("notifications/", include("entity.api.notifications")),
    path("update-info", update_entity_info, name="entity-update-info"),
    path("stats", get_entity_stats, name="entity-stats"),
    path("search-company", search_company, name="entity-search-company"),
]

from django.urls import path, include

from .update_info import update_entity_info
from .stats import get_entity_stats


urlpatterns = [
    path("admin/", include("entity.api_old.admin")),
    # path("depots/", include("entity.api_old.depots")),
    # path("production-sites/", include("entity.api_old.production_sites")),
    # path("users/", include("entity.api_old.users")),
    # path("certificates/", include("entity.api_old.certificates")),
    # path("options/", include("entity.api_old.options")),
    # path("notifications/", include("entity.api_old.notifications")),
    # path("registration/", include("entity.api_old.registration")),
    # path("update-info", update_entity_info, name="entity-update-info"),
    # path("stats", get_entity_stats, name="entity-stats"),
]

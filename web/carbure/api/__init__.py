from django.urls import path, include

from .home_stats import get_home_stats
from .metabase_status import get_metabase_status
from .nav_stats import get_nav_stats

urlpatterns = [
    path("auth/", include("auth.urls")),
    path("double-counting/", include("doublecount.urls")),
    path("entities/", include("entity.urls")),
    path("saf/", include("saf.urls")),
    path("resources/", include("resources.urls")),
    path("transactions/", include("transactions.api")),
    path("user/", include("user.urls")),
    path("elec/", include("elec.urls")),
    path("home-stats", get_home_stats, name="carbure-home-stats"),
    path("metabase-status", get_metabase_status, name="carbure-metabase-status"),
    path("tiruert/", include("tiruert.urls")),
    path("biomethane/", include("biomethane.urls")),
    path("feedstocks/", include("feedstocks.urls")),
    path("nav-stats", get_nav_stats, name="carbure-nav-stats"),
]

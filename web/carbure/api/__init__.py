from django.urls import path, include
from .home_stats import get_home_stats

urlpatterns = [
    path("apikey/", include("apikey.urls")),
    path("auth/", include("auth.api")),
    path("double-counting/", include("doublecount.api")),
    path("entity/", include("entity.api")),
    path("entities/", include("entity.urls")),
    path("saf/", include("saf.urls")),
    path("resources/", include("resources.api")),
    # path("transactions/", include("transactions.api")),
    path("transactions/", include("transactions.urls")),
    path("user/", include("user.api")),
    path("elec/", include("elec.api")),
    # path("elec/", include("elec.urls")),
    path("home-stats", get_home_stats, name="carbure-home-stats"),
]

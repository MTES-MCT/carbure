from django.urls import path, include
from .home_stats import get_home_stats

urlpatterns = [
    path("auth/", include("auth.urls")),
    path("double-counting/", include("doublecount.urls")),
    path("apikey/", include("apikey.urls")),
    path("entity/", include("entity.api")),
    path("entities/", include("entity.urls")),
    path("saf/", include("saf.urls")),
    path("resources/", include("resources.urls")),
    path("transactions/", include("transactions.api")),
    path("user/", include("user.urls")),
    path("v2/transactions/", include("transactions.urls")),
    path("elec/", include("elec.api")),
    # path("elec/", include("elec.urls")),
    path("home-stats", get_home_stats, name="carbure-home-stats"),
]

from django.urls import path, include
from .home_stats import get_home_stats

urlpatterns = [
    path("auth/", include("auth.api")),
    path("double-counting/", include("doublecount.api")),
    path("entity/", include("entity.api")),
    path("saf/", include("saf.urls")),
    path("resources/", include("resources.api")),
    path("transactions/", include("transactions.api")),
    path("user/", include("user.api")),
    path("elec/", include("elec.api")),
    path("home-stats", get_home_stats, name="carbure-home-stats"),
]

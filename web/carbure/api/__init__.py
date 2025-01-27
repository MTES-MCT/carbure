from django.urls import path, include
from rest_framework_nested.routers import SimpleRouter
from .home_stats import get_home_stats
from .nav_stats import get_nav_stats

urlpatterns = [
    path("auth/", include("auth.urls")),
    path("double-counting/", include("doublecount.urls")),
    path("entity/", include("entity.api")),
    path("entities/", include("entity.urls")),
    path("saf/", include("saf.urls")),
    path("resources/", include("resources.urls")),
    path("transactions/", include("transactions.api")),
    path("user/", include("user.urls")),
    path("elec/", include("elec.api")),
    path("home-stats", get_home_stats, name="carbure-home-stats"),
    path("nav-stats", get_nav_stats, name="carbure-nav-stats"),
    path("tiruert/", include("tiruert.urls")),
]

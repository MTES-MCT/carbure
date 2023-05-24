from django.urls import path, include
from .home_stats import get_home_stats

urlpatterns = [
    path("v3/doublecount/", include("doublecount.api.urls")),
    path("v5/admin/", include("admin.api")),
    path("v5/auth/", include("auth.api")),
    path("v5/audit/", include("audit.api")),
    path("v5/double-counting/", include("doublecount.api")),
    path("v5/entity/", include("entity.api")),
    path("v5/saf/", include("saf.api")),
    path("v5/resources/", include("resources.api")),
    path("v5/transactions/", include("transactions.api")),
    path("v5/user/", include("user.api")),
    path("v5/home-stats", get_home_stats, name="carbure-home-stats"),
]

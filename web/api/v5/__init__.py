from django.urls import path, include

urlpatterns = [
    path("admin/", include("admin.api")),
    path("admin/", include("api.v5.admin")),
    path("auth/", include("auth.api")),
    path("double-counting/", include("api.v5.double_counting")),
    path("entity/", include("entity.api")),
    path("saf/", include("api.v5.saf")),
    path("resources/", include("resources.api")),
    path("settings/", include("api.v5.settings")),
    path("stats/", include("api.v5.stats")),
    path("stats/", include("stats.api")),
    path("transactions/", include("transactions.api")),
    path("user/", include("user.api")),
]

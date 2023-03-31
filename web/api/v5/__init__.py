from django.urls import path, include

urlpatterns = [
    path("saf/", include("api.v5.saf")),
    path("stats/", include("api.v5.stats")),
    path("double-counting/", include("api.v5.double_counting")),
    path("admin/", include("api.v5.admin")),
    path("settings/", include("api.v5.settings")),
    path("declarations/", include("api.v5.declarations")),
    path("transactions/", include("transactions.api")),
    path("admin/", include("admin.api")),
]

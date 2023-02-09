from django.urls import path, include

urlpatterns = [
    path("saf/", include("api.v5.saf")),
    path("stats/", include("api.v5.stats")),
    path("admin/", include("api.v5.admin")),
    path("settings/", include("api.v5.settings")),
]

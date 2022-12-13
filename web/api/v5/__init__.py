from django.urls import path, include

urlpatterns = [
    path("saf/", include("api.v5.saf")),
    path("stats/", include("api.v5.stats")),
    path("admin/", include("api.v5.admin")),
    path("transactions/", include("api.v5.transactions")),
]

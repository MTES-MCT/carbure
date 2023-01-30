from django.urls import path, include

urlpatterns = [
    path("saf/", include("api.v5.saf")),
    path("stats/", include("api.v5.stats")),
    path("double-counting/", include("api.v5.double_counting")),
    path("admin/", include("api.v5.admin")),
    path("declarations/", include("api.v5.declarations")),
]

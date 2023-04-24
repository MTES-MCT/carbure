from django.urls import path, include

urlpatterns = [
    path("depots/", include("entity.api.depots")),
    path("production-sites/", include("entity.api.production_sites")),
    path("users/", include("entity.api.users")),
    path("users/", include("entity.api.users")),
    path("options/", include("entity.api.options")),
]

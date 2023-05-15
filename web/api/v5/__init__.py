from django.urls import path, include

urlpatterns = [
    path("admin/", include("admin.api")),
    path("auth/", include("auth.api")),
    path("double-counting/", include("api.v5.double_counting")),
    path("entity/", include("entity.api")),
    path("saf/", include("saf.api")),
    path("resources/", include("resources.api")),
    path("stats/", include("stats.api")),
    path("transactions/", include("transactions.api")),
    path("user/", include("user.api")),
]

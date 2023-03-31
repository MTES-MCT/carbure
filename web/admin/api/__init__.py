from django.urls import path, include

urlpatterns = [
    path("map/", include("admin.api.map")),
    path("dashboard/", include("admin.api.dashboard")),
    path("entities/", include("admin.api.entities")),
]

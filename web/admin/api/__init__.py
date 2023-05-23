from django.urls import path, include

urlpatterns = [
    path("map/", include("admin.api.map")),  # TODO rename flow-map
    path("dashboard/", include("admin.api.dashboard")),
    path("entities/", include("admin.api.entities")),
    path("lots/", include("admin.api.lots")),
    path("controls/", include("admin.api.controls")),
]

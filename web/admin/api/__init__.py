from django.urls import path, include

urlpatterns = [
    path("dashboard/", include("admin.api.dashboard")),
    path("entities/", include("admin.api.entities")),
    path("controls/", include("admin.api.controls")),
]

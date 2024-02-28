from django.urls import path, include

urlpatterns = [
    path("entities/", include("admin.api.entities")),
    path("controls/", include("admin.api.controls")),
]

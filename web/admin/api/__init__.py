from django.urls import path, include

urlpatterns = [
    path("map/", include("admin.api.map")),
]

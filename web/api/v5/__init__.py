from django.urls import path, include

urlpatterns = [
    path("saf/", include("api.v5.saf")),
]

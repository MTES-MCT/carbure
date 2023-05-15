from django.urls import path, include

urlpatterns = [
    path("operator/", include("api.v5.saf.operator")),
    path("airline/", include("api.v5.saf.airline")),
]

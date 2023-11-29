from django.urls import path, include

urlpatterns = [
    path("applications/", include("doublecount.api.applications")),
    path("agreements/", include("doublecount.api.agreements")),
]

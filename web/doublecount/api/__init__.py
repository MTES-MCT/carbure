from django.urls import path, include

urlpatterns = [
    path("application/", include("doublecount.api.application")),
    path("agreements/", include("doublecount.api.agreements")),
]

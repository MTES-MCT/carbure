from django.urls import path, include

urlpatterns = [
    path("admin/", include("doublecount.api.admin")),
    path("applications/", include("doublecount.api.applications")),
    path("agreements/", include("doublecount.api.agreements")),
]

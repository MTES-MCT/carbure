from django.urls import path, include

urlpatterns = [
    path("applications/", include("admin.api.double_counting.applications")),
]

from django.urls import path, include

urlpatterns = [
    path("agreements/", include("admin.api.double_counting.agreements")),
    path("application/", include("admin.api.double_counting.application")),
]

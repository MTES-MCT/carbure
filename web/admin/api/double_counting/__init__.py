from django.urls import path, include

urlpatterns = [
    path("application/", include("admin.api.double_counting.application")),
]

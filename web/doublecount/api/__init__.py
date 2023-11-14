from django.urls import path, include

urlpatterns = [
    path("application/", include("doublecount.api.application")),
    path("agreement/", include("doublecount.api.agreement")),
]

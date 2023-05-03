from django.urls import path, include

urlpatterns = [
    path("v3/doublecount/", include("doublecount.api.urls")),
    path("", include("api.v4.urls")),
    path("v5/", include("api.v5")),
]

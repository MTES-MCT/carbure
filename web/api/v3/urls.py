from django.urls import path, include

urlpatterns = [
    path("doublecount/", include("api.v3.doublecount.urls")),
]

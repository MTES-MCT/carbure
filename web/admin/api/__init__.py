from django.urls import path, include

urlpatterns = [
    path("controls/", include("admin.api.controls")),
]

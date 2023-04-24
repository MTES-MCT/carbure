from django.urls import path, include

urlpatterns = [
    path("settings/", include("api.v3.settings.urls")),
    path("auditor/", include("api.v3.auditor.urls")),
    path("doublecount/", include("api.v3.doublecount.urls")),
]

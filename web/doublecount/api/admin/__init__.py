from django.urls import path, include
from .snapshot import get_snapshot

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="doublecount.api.admin.snapshot"),
    path("applications/", include("doublecount.api.admin.applications")),
    path("agreements/", include("doublecount.api.admin.agreements")),
]

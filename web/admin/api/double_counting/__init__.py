from django.urls import path, include
from .snapshot import get_snapshot

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="admin.api.double_counting.snapshot"),
    path("applications/", include("admin.api.double_counting.applications")),
]

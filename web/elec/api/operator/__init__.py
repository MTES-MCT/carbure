from django.urls import path
from .snapshot import get_snapshot

urlpatterns = [
    # overview
    path("snapshot", get_snapshot, name="elec-snapshot"),
]

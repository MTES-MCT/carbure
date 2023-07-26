from django.urls import path, include
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="admin-elec-years"),
    path("snapshot", get_snapshot, name="admin-elec-snapshot"),
]

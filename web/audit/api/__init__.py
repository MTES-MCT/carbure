from django.urls import path
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="controls-years"),
    path("snapshot", get_snapshot, name="controls-snapshot"),
]

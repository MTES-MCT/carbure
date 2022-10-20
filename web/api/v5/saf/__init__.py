from django.urls import path

from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="api-v5-saf-years"),
    path("snapshot", get_snapshot, name="api-v5-saf-snapshot"),
]

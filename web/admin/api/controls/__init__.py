from django.urls import include, path
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="admin-controls-years"),
    path("snapshot", get_snapshot, name="admin-controls-snapshot"),
    path("lots/", include("admin.api.controls.lots")),
    path("stocks/", include("admin.api.controls.stocks")),
]

from django.urls import include, path
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="audit-years"),
    path("snapshot", get_snapshot, name="audit-snapshot"),
    path("lots/", include("audit.api.lots")),
    path("stocks/", include("audit.api.stocks")),
]

from django.urls import include, path
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="transactions-audit-years"),
    path("snapshot", get_snapshot, name="transactions-audit-snapshot"),
    path("lots/", include("transactions.api.audit.lots")),
    path("stocks/", include("transactions.api.audit.stocks")),
]

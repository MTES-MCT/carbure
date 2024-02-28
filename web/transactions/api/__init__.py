from django.urls import path, include
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("snapshot", get_snapshot, name="transactions-snapshot"),
    path("years", get_years, name="transactions-years"),
    path("audit/", include("transactions.api.audit")),
    path("admin/", include("transactions.api.admin")),
    path("lots/", include("transactions.api.lots")),
    path("stocks/", include("transactions.api.stocks")),
    path("declarations/", include("transactions.api.declarations")),
]

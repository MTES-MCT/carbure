from django.urls import include, path
from transactions.api.admin.snapshot import get_snapshot
from transactions.api.admin.years import get_years
from transactions.api.admin.declarations import get_declarations
from .map import map

urlpatterns = [
    path("lots/", include("transactions.api.admin.lots")),
    path("stocks/", include("transactions.api.admin.stocks")),
    path("flow-map", map, name="transactions-admin-flow-map"),
    path("years", get_years, name="transactions-admin-controls-years"),
    path("snapshot", get_snapshot, name="transactions-admin-controls-snapshot"),
    path("declarations", get_declarations, name="transactions-admin-declarations"),
]

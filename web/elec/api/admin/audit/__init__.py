from django.urls import include, path
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="elec-admin-audit-years"),
    path("snapshot", get_snapshot, name="elec-admin-audit-snapshot"),
    path("charge-points/", include("elec.api.admin.audit.charge_points")),
]

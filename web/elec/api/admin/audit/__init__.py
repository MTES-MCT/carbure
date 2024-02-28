from django.urls import include, path
from .years import get_years
from .snapshot import get_snapshot

urlpatterns = [
    path("years", get_years, name="elec-admin-transactions-audit-years"),
    path("snapshot", get_snapshot, name="elec-admin-transactions-audit-snapshot"),
    path("charge-points/", include("elec.api.admin.audit.charge_points")),
    path("meter-readings/", include("elec.api.admin.audit.meter_readings")),
]

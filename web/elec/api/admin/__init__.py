from django.urls import path, include


from .years import get_years
from .snapshot import get_snapshot


urlpatterns = [
    path("years", get_years, name="admin-elec-years"),
    path("snapshot", get_snapshot, name="admin-elec-snapshot"),
    path("transfer-certificates/", include("elec.api.admin.transfer_certificates")),
    path("provision-certificates/", include("elec.api.admin.provision_certificates")),
    path("audit/", include("elec.api.admin.audit")),
    path("charge-points/", include("elec.api.admin.charge_points")),
    path("meter-readings/", include("elec.api.admin.meter_readings")),
]

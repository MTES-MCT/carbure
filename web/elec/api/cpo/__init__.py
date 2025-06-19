from django.urls import include, path

from .charge_point_snapshot import get_charge_point_snapshot


urlpatterns = [
    # overview
    path("charge-point-snapshot", get_charge_point_snapshot, name="elec-cpo-charge-point-snapshot"),
    path("charge-points/", include("elec.api.cpo.charge_points")),
    path("meter-readings/", include("elec.api.cpo.meter_readings")),
    path("meters/", include("elec.api.cpo.meters")),
]

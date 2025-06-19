from django.urls import path, include



urlpatterns = [
    path("audit/", include("elec.api.admin.audit")),
    path("charge-points/", include("elec.api.admin.charge_points")),
    path("meter-readings/", include("elec.api.admin.meter_readings")),
]

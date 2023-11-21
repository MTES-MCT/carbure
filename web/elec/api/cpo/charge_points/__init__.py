from django.urls import include, path

from .check_charge_point_application import check_charge_point_application

urlpatterns = [
    path("check-application", check_charge_point_application, name="elec-cpo-charge-points-check-application"),
]

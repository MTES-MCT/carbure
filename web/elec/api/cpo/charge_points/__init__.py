from django.urls import path


from .charge_points import get_charge_points
from .charge_point_details import get_charge_point_details
from .applications import get_applications
from .application_details import get_application_details
from .check_application import check_application
from .add_application import add_application
from .update_charge_point import update_charge_point

urlpatterns = [
    path("", get_charge_points, name="elec-cpo-charge-points-get-charge-points"),
    path("applications", get_applications, name="elec-cpo-charge-points-get-applications"),
    path("application-details", get_application_details, name="elec-cpo-charge-points-get-application-details"),
    path("check-application", check_application, name="elec-cpo-charge-points-check-application"),
    path("add-application", add_application, name="elec-cpo-charge-points-add-application"),
    path("details", get_charge_point_details, name="elec-admin-charge-points-get-charge-point-details"),
    path("update", update_charge_point, name="elec-admin-charge-points-update-charge-point"),
]

from django.urls import path

from .charge_points import get_charge_points
from .charge_point_details import get_charge_point_details
from .applications import get_applications
from .application_details import get_application_details
from .check_application import check_application
from .add_application import add_application
from .filters import get_charge_points_filters
from .update_charge_point import update_charge_point
from .update_prm import update_prm
from .delete_charge_point import delete_charge_point

urlpatterns = [
    path("", get_charge_points, name="elec-cpo-charge-points-get-charge-points"),
    path("applications", get_applications, name="elec-cpo-charge-points-get-applications"),
    path("application-details", get_application_details, name="elec-cpo-charge-points-get-application-details"),
    path("check-application", check_application, name="elec-cpo-charge-points-check-application"),
    path("add-application", add_application, name="elec-cpo-charge-points-add-application"),
    path("filters", get_charge_points_filters, name="elec-cpo-charge-points-filters"),
    path("details", get_charge_point_details, name="elec-cpo-charge-points-get-charge-point-details"),
    path("update-charge-point", update_charge_point, name="elec-cpo-charge-points-update-charge-point"),
    path("update-prm", update_prm, name="elec-cpo-charge-points-update-prm"),
    path("delete", delete_charge_point, name="elec-cpo-charge-points-delete-charge-point"),
]

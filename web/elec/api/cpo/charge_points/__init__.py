from django.urls import path


from .charge_points import get_charge_points
from .applications import get_applications
from .application_details import get_application_details
from .check_application import check_application
from .add_application import add_application

urlpatterns = [
    path("", get_charge_points, name="elec-cpo-charge-points-get-charge-points"),
    path("applications", get_applications, name="elec-cpo-charge-points-get-applications"),
    path("application-details", get_application_details, name="elec-cpo-charge-points-get-application-details"),
    path("check-application", check_application, name="elec-cpo-charge-points-check-application"),
    path("add-application", add_application, name="elec-cpo-charge-points-add-application"),
]

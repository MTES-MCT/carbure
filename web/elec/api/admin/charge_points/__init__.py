from django.urls import path


from .charge_points import get_charge_points
from .applications import get_applications
from .application_details import get_application_details

urlpatterns = [
    path("", get_charge_points, name="elec-admin-charge-points-get-charge-points"),
    path("applications", get_applications, name="elec-admin-charge-points-get-applications"),
    path("application-details", get_application_details, name="elec-admin-charge-points-get-application-details"),
]

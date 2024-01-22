from django.urls import path


from .charge_points import get_charge_points
from .applications import get_applications
from .application_details import get_application_details
from .accept_application import accept_application
from .reject_application import reject_application

urlpatterns = [
    path("", get_charge_points, name="elec-admin-charge-points-get-charge-points"),
    path("applications", get_applications, name="elec-admin-charge-points-get-applications"),
    path("application-details", get_application_details, name="elec-admin-charge-points-get-application-details"),
    path("accept-application", accept_application, name="elec-admin-charge-points-accept-application"),
    path("reject-application", reject_application, name="elec-admin-charge-points-reject-application"),
]

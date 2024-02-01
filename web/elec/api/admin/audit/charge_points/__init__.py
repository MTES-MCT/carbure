from django.urls import path
from .applications import get_applications
from .filters import get_charge_points_applications_filters
from .application_details import get_application_details
from .accept_application import accept_application
from .reject_application import reject_application

urlpatterns = [
    path("applications", get_applications, name="elec-admin-audit-charge-points-applications"),
    path("filters", get_charge_points_applications_filters, name="elec-admin-audit-charge-points-filters"),
    path("application-details", get_application_details, name="elec-admin-audit-charge-points-application-details"),
    path("accept-application", accept_application, name="elec-admin-audit-charge-points-accept-application"),
    path("reject-application", reject_application, name="elec-admin-audit-charge-points-reject-application"),
    # path("start-audit", get_application_details, name="elec-admin-audit-charge-points-application-details"),
]

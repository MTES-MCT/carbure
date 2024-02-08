from django.urls import path

from .applications import get_applications
from .filters import get_meter_readings_applications_filters

from .application_details import get_application_details

# from .accept_application import accept_application
# from .reject_application import reject_application
# from .start_audit import start_audit

urlpatterns = [
    path("applications", get_applications, name="elec-admin-audit-meter-readings-applications"),
    path("filters", get_meter_readings_applications_filters, name="elec-admin-audit-meter-readings-filters"),
    path("application-details", get_application_details, name="elec-admin-audit-meter-readings-application-details"),
    # path("accept-application", accept_application, name="elec-admin-audit-charge-points-accept-application"),
    # path("reject-application", reject_application, name="elec-admin-audit-charge-points-reject-application"),
    # path("start-audit", start_audit, name="elec-admin-audit-charge-points-start-audit"),
]
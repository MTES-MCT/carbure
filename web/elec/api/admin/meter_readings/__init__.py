from django.urls import path

from .applications import get_applications
from .application_details import get_application_details
from .accept_application import accept_application
from .reject_application import reject_application

urlpatterns = [
    path("applications", get_applications, name="admin-elec-meter-readings-get-applications"),
    path("application-details", get_application_details, name="admin-elec-meter-readings-get-application-details"),
    path("accept-application", accept_application, name="admin-elec-meter-readings-accept-application"),
    path("reject-application", reject_application, name="admin-elec-meter-readings-reject-application"),
]

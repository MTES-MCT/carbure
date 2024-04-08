from django.urls import path

from .applications import get_applications
from .application_details import get_application_details

urlpatterns = [
    path("applications", get_applications, name="admin-elec-meter-readings-get-applications"),
    path("application-details", get_application_details, name="admin-elec-meter-readings-get-application-details"),
]

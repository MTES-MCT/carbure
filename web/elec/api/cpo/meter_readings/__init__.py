from django.urls import path


from .application_template import get_application_template
from .application_details import get_application_details
from .check_application import check_application
from .add_application import add_application
from .applications import get_applications

urlpatterns = [
    path("application-template", get_application_template, name="elec-cpo-meter-readings-get-application-template"),
    path("application-details", get_application_details, name="elec-cpo-meter-readings-get-application-details"),
    path("check-application", check_application, name="elec-cpo-meter-readings-check-application"),
    path("add-application", add_application, name="elec-cpo-meter-readings-add-application"),
    path("applications", get_applications, name="elec-cpo-meter-readings-get-applications"),
]

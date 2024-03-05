from django.urls import path
from .check_file import check_file
from .application_details import get_application_details
from .add_application import add_application

urlpatterns = [
    path("details", get_application_details, name="doublecount-applications-details"),
    path("check-file", check_file, name="doublecount-applications-check-file"),
    path("add", add_application, name="doublecount-applications-add-application"),
]

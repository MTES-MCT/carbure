from django.urls import path
from .check_file import check_file
from .application_details import get_application_details


urlpatterns = [
    path("details", get_application_details, name="doublecount-applications-details"),
    path("check-file", check_file, name="doublecount-applications-check-file"),
]

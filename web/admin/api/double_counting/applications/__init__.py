from django.urls import path
from .check_files import check_files
from .add import add_application
from .applications import get_applications_admin
from .application import get_application

urlpatterns = [
    path("check-files", check_files, name="admin-double-counting-application-check-files"),
    path("add", add_application, name="admin-double-counting-application-add"),
    path("", get_applications_admin, name="admin-double-counting-applications"),
    path("details", get_application, name="admin-double-counting-application-details"),
]

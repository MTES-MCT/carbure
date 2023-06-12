from django.urls import path
from .check_files import check_files
from .add import add_application

urlpatterns = [
    path("check-files", check_files, name="admin-double-counting-application-check-files"),
    path("add", add_application, name="admin-double-counting-application-add"),
]

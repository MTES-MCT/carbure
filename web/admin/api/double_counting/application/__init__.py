from django.urls import path
from .check_files import check_files

urlpatterns = [
    path("check-files", check_files, name="admin-double-counting-application-check-files"),
]

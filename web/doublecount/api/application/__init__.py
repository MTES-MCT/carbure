from django.urls import path
from .check_file import check_file


urlpatterns = [
    path("check-file", check_file, name="admin-double-counting-application-check-files"),
]

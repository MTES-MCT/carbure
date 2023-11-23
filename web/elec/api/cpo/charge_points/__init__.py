from django.urls import path

from .check_application import check_application
from .add_application import add_application

urlpatterns = [
    path("check-application", check_application, name="elec-cpo-charge-points-check-application"),
    path("add-application", add_application, name="elec-cpo-charge-points-add-application"),
]

from django.urls import path

from .applications import get_applications
from .accept_application import accept_application
from .reject_application import reject_application

urlpatterns = [
    path("applications", get_applications, name="admin-elec-charge-points-get-applications"),
    path("accept-application", accept_application, name="admin-elec-charge-points-accept-application"),
    path("reject-application", reject_application, name="admin-elec-charge-points-reject-application"),
]

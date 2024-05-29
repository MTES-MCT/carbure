from django.urls import path

from .years import get_years
from .snapshot import get_snapshot
from .applications import get_applications
from .application_details import get_application_details
from .filters import get_application_filters
from .get_sample import get_sample


urlpatterns = [
    path("years", get_years, name="elec-audit-years"),
    path("snapshot", get_snapshot, name="elec-audit-snapshot"),
    path("applications", get_applications, name="elec-audit-applications"),
    path("filters", get_application_filters, name="elec-audit-filters"),
    path("application-details", get_application_details, name="elec-audit-application-details"),
    path("get-sample", get_sample, name="elec-audit-get-sample"),
]

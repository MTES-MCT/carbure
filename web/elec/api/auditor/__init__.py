from django.urls import path


from .years import get_years
from .snapshot import get_snapshot
from .applications import get_applications
from .application_details import get_application_details
from .filters import get_application_filters
from .get_sample import get_sample
from .check_report import check_report
from .accept_report import accept_report


urlpatterns = [
    path("years", get_years, name="elec-auditor-years"),
    path("snapshot", get_snapshot, name="elec-auditor-snapshot"),
    path("applications", get_applications, name="elec-auditor-applications"),
    path("filters", get_application_filters, name="elec-auditor-filters"),
    path("application-details", get_application_details, name="elec-auditor-application-details"),
    path("get-sample", get_sample, name="elec-auditor-get-sample"),
    path("check-report", check_report, name="elec-auditor-check-report"),
    path("accept-report", accept_report, name="elec-auditor-accept-report"),
]

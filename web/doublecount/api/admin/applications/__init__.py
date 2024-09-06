from django.urls import path
from .check_files import check_files
from .add import add_application
from .applications import get_applications_admin
from .application import get_application_details
from .update_quotas import update_approved_quotas
from .reject_application import reject_dca
from .approve_application import approve_dca
from .export_application import export_dca


urlpatterns = [
    path("", get_applications_admin, name="admin-double-counting-applications"),
    path("details", get_application_details, name="admin-double-counting-application-details"),
    path("check-files", check_files, name="admin-double-counting-application-check-files"),
    path("add", add_application, name="admin-double-counting-application-add"),
    path("update-approved-quotas", update_approved_quotas, name="admin-double-counting-application-update-approved-quotas"),
    path("approve", approve_dca, name="admin-double-counting-application-approve"),
    path("reject", reject_dca, name="admin-double-counting-application-reject"),
    path("export", export_dca, name="admin-double-counting-application-export"),
]

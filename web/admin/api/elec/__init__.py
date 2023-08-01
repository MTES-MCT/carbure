from django.urls import path, include


from .years import get_years
from .snapshot import get_snapshot
from .import_certificates import import_certificate_excel
from .provision_certificates import get_provision_certificates

urlpatterns = [
    path("years", get_years, name="admin-elec-years"),
    path("snapshot", get_snapshot, name="admin-elec-snapshot"),
    path("import-certificates", import_certificate_excel, name="admin-elec-import-certificates"),
    path("provision-certificates", get_provision_certificates, name="admin-elec-get-provision-certificates"),
]

from django.urls import path, include

from .years import get_years
from .snapshot import get_snapshot
from admin.api.elec.import_certificates import import_certificate_excel

urlpatterns = [
    path("years", get_years, name="admin-elec-years"),
    path("snapshot", get_snapshot, name="admin-elec-snapshot"),
    path("import-certificates", import_certificate_excel, name="admin-elec-import-certificates"),
]

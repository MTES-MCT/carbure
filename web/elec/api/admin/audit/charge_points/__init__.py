from django.urls import path
from .applications import get_applications

urlpatterns = [
    path("applications", get_applications, name="elec-admin-audit-charge-points-applications"),
]

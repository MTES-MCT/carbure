from django.urls import path
from .years import get_years

urlpatterns = [
    path("years", get_years, name="elec-admin-audit-years"),
    path("", get_years, name="elec-admin-audit-years"),
]

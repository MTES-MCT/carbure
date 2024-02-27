from django.urls import path

from .agreements import get_agreements
from .agreement_details import get_agreement_details


urlpatterns = [
    path("", get_agreements, name="admin-double-counting-agreements"),
    path("details", get_agreement_details, name="admin-double-counting-agreements-details"),
]

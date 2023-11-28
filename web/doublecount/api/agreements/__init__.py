from django.urls import path

from .agreements import get_agreements
from .agreement_details import get_agreement_details


urlpatterns = [
    path("details", get_agreement_details, name="doublecount-agreements-details"),
    path("", get_agreements, name="doublecount-agreements"),
]

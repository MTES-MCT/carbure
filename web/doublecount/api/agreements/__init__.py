from django.urls import path

from .agreements import get_agreements
from .agreement_details import get_agreement_details
from .agreements_public_list import get_agreements_public_list


urlpatterns = [
    path("details", get_agreement_details, name="doublecount-agreements-details"),
    path("", get_agreements, name="doublecount-agreements"),
    path("public-list", get_agreements_public_list, name="doublecount-agreements-public-list"),
]

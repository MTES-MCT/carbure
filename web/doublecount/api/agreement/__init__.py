from django.urls import path

from doublecount.api.agreement.agreements import get_agreements


urlpatterns = [
    path("agreements", get_agreements, name="doublecount-agreements"),
]

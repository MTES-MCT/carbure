from django.urls import path

from doublecount.api.agreements.agreements import get_agreements


urlpatterns = [
    path("", get_agreements, name="doublecount-agreements"),
]

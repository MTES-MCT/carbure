from django.urls import path

from .agreements import get_agreements


urlpatterns = [
    path("", get_agreements, name="admin-double-counting-agreements"),
]

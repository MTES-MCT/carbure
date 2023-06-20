from django.urls import path
from .agreements import get_agreements_admin

urlpatterns = [
    path("", get_agreements_admin, name="admin-double-counting-agreements"),
]

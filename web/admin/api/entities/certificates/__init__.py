from django.urls import path
from .certificates import get_entity_certificates
from .check import check_entity_certificate
from .reject import reject_entity_certificate

urlpatterns = [
    path("", get_entity_certificates, name="admin-entities-certificates"),
    path("check", check_entity_certificate, name="admin-entities-certificates-check"),
    path("reject", reject_entity_certificate, name="admin-entities-certificates-reject"),
]

from django.urls import path
from .certificates import get_my_certificates
from .set_default import set_default_certificate
from .add import add_certificate
from .delete import delete_certificate
from .update import update_certificate


urlpatterns = [
    path("", get_my_certificates, name="entity-certificates"),
    path("add", add_certificate, name="entity-certificates-add"),
    path("delete", delete_certificate, name="entity-certificates-delete"),
    path("update", update_certificate, name="entity-certificates-update"),
    path("set-default", set_default_certificate, name="entity-certificates-set-default"),
]

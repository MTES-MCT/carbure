from django.urls import path
from .user import get_settings
from .request_access import request_entity_access
from .revoke_access import revoke_myself

urlpatterns = [
    path("", get_settings, name="user"),
    path("request-access", request_entity_access, name="user-request-access"),
    path("revoke-access", revoke_myself, name="user-revoke-access"),
]

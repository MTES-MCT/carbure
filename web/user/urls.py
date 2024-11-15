from django.urls import path

from user.views import get_settings, request_entity_access, revoke_myself

urlpatterns = [
    path("", get_settings, name="user"),
    path("request-access", request_entity_access, name="user-request-access"),
    path("revoke-access", revoke_myself, name="user-revoke-access"),
]

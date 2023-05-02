from django.urls import path
from . import views

urlpatterns = [
    # rights
    path("get-entity-rights", views.get_entity_rights, name="api-v3-settings-get-entity-rights"),
    path("invite-user", views.invite_user, name="api-v3-settings-invite-user"),
    path("accept-user", views.accept_user, name="api-v3-settings-access-user"),
    path("revoke-user", views.revoke_user, name="api-v3-settings-revoke-user"),
    path("entity-hash", views.get_entity_hash, name="api-v3-settings-entity-hash"),
]

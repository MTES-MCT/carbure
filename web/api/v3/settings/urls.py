from django.urls import path
from . import views

urlpatterns = [
    path("rfc", views.toggle_rfc, name="api-v3-settings-rfc"),
    path("trading", views.toggle_trading, name="api-v3-settings-trading"),
    path("stocks", views.toggle_stocks, name="api-v3-settings-stocks"),
    path("direct-deliveries", views.toggle_direct_deliveries, name="api-v3-settings-direct-deliveries"),
    # rights
    path("get-entity-rights", views.get_entity_rights, name="api-v3-settings-get-entity-rights"),
    path("invite-user", views.invite_user, name="api-v3-settings-invite-user"),
    path("accept-user", views.accept_user, name="api-v3-settings-access-user"),
    path("revoke-user", views.revoke_user, name="api-v3-settings-revoke-user"),
    path("entity-hash", views.get_entity_hash, name="api-v3-settings-entity-hash"),
]

from django.urls import path
from . import views

urlpatterns = [
    path("enable-mac", views.enable_mac, name="api-v3-settings-enable-mac"),
    path("disable-mac", views.disable_mac, name="api-v3-settings-disable-mac"),
    path("enable-trading", views.enable_trading, name="api-v3-settings-enable-trading"),
    path("disable-trading", views.disable_trading, name="api-v3-settings-disable-trading"),
    path("enable-stocks", views.enable_stocks, name="api-v3-settings-enable-stocks"),
    path("disable-stocks", views.disable_stocks, name="api-v3-settings-disable-stocks"),
    path("enable-direct-deliveries", views.enable_direct_deliveries, name="api-v3-settings-enable-direct-deliveries"),
    path(
        "disable-direct-deliveries", views.disable_direct_deliveries, name="api-v3-settings-disable-direct-deliveries"
    ),
    # path("get-production-sites", views.get_production_sites, name="api-v3-settings-get-production-sites"),
    # path("add-production-site", views.add_production_site, name="api-v3-settings-add-production-site"),
    # path("delete-production-site", views.delete_production_site, name="api-v3-settings-delete-production-site"),
    # path("update-production-site", views.update_production_site, name="api-v3-settings-update-production-site"),
    # path(
    #     "set-production-site-matieres-premieres",
    #     views.set_production_site_mp,
    #     name="api-v3-settings-set-production-site-matieres-premieres",
    # ),
    # path(
    #     "set-production-site-biocarburants",
    #     views.set_production_site_bc,
    #     name="api-v3-settings-set-production-site-biocarburants",
    # ),
    # path("get-delivery-sites", views.get_delivery_sites, name="api-v3-settings-get-delivery-sites"),
    # path("add-delivery-site", views.add_delivery_site, name="api-v3-settings-add-delivery-site"),
    # path("delete-delivery-site", views.delete_delivery_site, name="api-v3-settings-delete-delivery-site"),
    # rights
    path("get-entity-rights", views.get_entity_rights, name="api-v3-settings-get-entity-rights"),
    path("invite-user", views.invite_user, name="api-v3-settings-invite-user"),
    path("accept-user", views.accept_user, name="api-v3-settings-access-user"),
    path("revoke-user", views.revoke_user, name="api-v3-settings-revoke-user"),
    path("entity-hash", views.get_entity_hash, name="api-v3-settings-entity-hash"),
]

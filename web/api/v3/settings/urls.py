from django.urls import path
from . import views

urlpatterns = [
     path('', views.get_settings, name='api-v3-settings-get'),

     path('update-entity', views.update_entity, name='api-v3-settings-update-entity'),


     path('enable-mac', views.enable_mac, name='api-v3-settings-enable-mac'),
     path('disable-mac', views.disable_mac, name='api-v3-settings-disable-mac'),
     path('enable-trading', views.enable_trading, name='api-v3-settings-enable-trading'),
     path('disable-trading', views.disable_trading, name='api-v3-settings-disable-trading'),

     path('get-production-sites', views.get_production_sites, name='api-v3-settings-get-production-sites'),
     path('add-production-site', views.add_production_site, name='api-v3-settings-add-production-site'),
     path('delete-production-site', views.delete_production_site, name='api-v3-settings-delete-production-site'),
     path('update-production-site', views.update_production_site, name='api-v3-settings-update-production-site'),
     path('set-production-site-matieres-premieres', views.set_production_site_mp,
          name='api-v3-settings-set-production-site-matieres-premieres'),
     path('set-production-site-biocarburants', views.set_production_site_bc,
          name='api-v3-settings-set-production-site-biocarburants'),

     path('get-delivery-sites', views.get_delivery_sites, name='api-v3-settings-get-delivery-sites'),
     path('add-delivery-site', views.add_delivery_site, name='api-v3-settings-add-delivery-site'),
     path('delete-delivery-site', views.delete_delivery_site, name='api-v3-settings-delete-delivery-site'),

     # ISCC
     path('get-iscc-certificates', views.get_iscc_certificates, name='api-v3-settings-get-iscc-certificates'),
     path('add-iscc-certificate', views.add_iscc_certificate, name='api-v3-settings-add-iscc-certificate'),
     path('delete-iscc-certificate', views.delete_iscc_certificate, name='api-v3-settings-delete-iscc-certificate'),
     path('update-iscc-certificate', views.update_iscc_certificate, name='api-v3-settings-update-iscc-certificate'),

     # 2BS
     path('get-2bs-certificates', views.get_2bs_certificates, name='api-v3-settings-get-2bs-certificates'),
     path('add-2bs-certificate', views.add_2bs_certificate, name='api-v3-settings-add-2bs-certificate'),
     path('delete-2bs-certificate', views.delete_2bs_certificate, name='api-v3-settings-delete-2bs-certificate'),
     path('update-2bs-certificate', views.update_2bs_certificate, name='api-v3-settings-update-2bs-certificate'),

     # REDCert
     path('get-redcert-certificates', views.get_redcert_certificates, name='api-v3-settings-get-redcert-certificates'),
     path('add-redcert-certificate', views.add_redcert_certificate, name='api-v3-settings-add-redcert-certificate'),
     path('delete-redcert-certificate', views.delete_redcert_certificate, name='api-v3-settings-delete-redcert-certificate'),
     path('update-redcert-certificate', views.update_redcert_certificate, name='api-v3-settings-update-redcert-certificate'),


     # SN / Systeme National
     path('get-sn-certificates', views.get_sn_certificates, name='api-v3-settings-get-sn-certificates'),
     path('add-sn-certificate', views.add_sn_certificate, name='api-v3-settings-add-sn-certificate'),
     path('delete-sn-certificate', views.delete_sn_certificate, name='api-v3-settings-delete-sn-certificate'),
     path('update-sn-certificate', views.update_sn_certificate, name='api-v3-settings-update-sn-certificate'),



     path('get-my-certificates', views.get_my_certificates, name='api-v3-settings-get-my-certificates'),
     path('set-production-site-certificates', views.set_production_site_certificates, name='api-v3-settings-set-production-site-certificates'),



     # rights
     path('request-entity-access', views.request_entity_access, name='api-v3-settings-request-entity-access'),
     path('get-entity-rights', views.get_entity_rights, name='api-v3-settings-get-entity-rights'),
     path('invite-user', views.invite_user, name='api-v3-settings-invite-user'),
     path('accept-user', views.accept_user, name='api-v3-settings-access-user'),
     path('revoke-user', views.revoke_user, name='api-v3-settings-revoke-user'),
     path('revoke-myself', views.revoke_myself, name='api-v3-settings-revoke-myself'),

]

from django.urls import path
from . import views

urlpatterns = [
     path('', views.get_settings, name='api-v3-settings-get'),

     path('enable-mac', views.enable_mac, name='api-v3-settings-enable-mac'),
     path('disable-mac', views.disable_mac, name='api-v3-settings-disable-mac'),
     path('enable-trading', views.enable_trading, name='api-v3-settings-enable-trading'),
     path('disable-trading', views.disable_trading, name='api-v3-settings-disable-trading'),
     path('set-national-system-certificate', views.set_national_system_certificate, name='api-v3-settings-set-national-system-certificate'),

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

     path('get-iscc-certificates', views.get_iscc_certificates, name='api-v3-settings-get-iscc-certificates'),
     path('get-2bs-certificates', views.get_2bs_certificates, name='api-v3-settings-get-2bs-certificates'),
     path('add-iscc-certificate', views.add_iscc_certificate, name='api-v3-settings-add-iscc-certificate'),
     path('add-2bs-certificate', views.add_2bs_certificate, name='api-v3-settings-add-2bs-certificate'),
     path('delete-iscc-certificate', views.delete_iscc_certificate, name='api-v3-settings-delete-iscc-certificate'),
     path('delete-2bs-certificate', views.delete_2bs_certificate, name='api-v3-settings-delete-2bs-certificate'),
     path('get-my-certificates', views.get_my_certificates, name='api-v3-settings-get-my-certificates'),
     path('add-production-site-certificate', views.add_production_site_certificate, name='api-v3-settings-add-production-site-certificate'),
     path('delete-production-site-certificate', views.delete_production_site_certificate, name='api-v3-settings-delete-production-site-certificate'),
     path('set-production-site-certificates', views.set_production_site_certificates, name='api-v3-settings-set-production-site-certificates'),
     path('update-iscc-certificate', views.update_iscc_certificate, name='api-v3-settings-update-iscc-certificate'),
     path('update-2bs-certificate', views.update_2bs_certificate, name='api-v3-settings-update-2bs-certificate'),

     path('request-entity-access', views.request_entity_access, name='api-v3-settings-request-entity-access'),
]

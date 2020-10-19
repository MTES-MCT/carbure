from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_settings, name='api-v3-settings-get'),
    path('add-production-site', views.add_production_site, name='api-v3-settings-add-production-site'),
    path('delete-production-site', views.delete_production_site, name='api-v3-settings-delete-production-site'),
    path('add-production-site-matiere-premiere', views.add_production_site_mp,
         name='api-v3-settings-add-production-site-matiere-premiere'),
    path('delete-production-site-matiere-premiere', views.delete_production_site_mp,
         name='api-v3-settings-delete-production-site-matiere-premiere'),
    path('add-production-site-biocarburant', views.add_production_site_bc,
         name='api-v3-settings-add-production-site-biocarburant'),
    path('delete-production-site-biocarburant', views.delete_production_site_bc,
         name='api-v3-settings-delete-production-site-biocarburant'),
    path('enable-mac', views.enable_mac, name='api-v3-settings-enable-mac'),
    path('disable-mac', views.disable_mac, name='api-v3-settings-disable-mac'),
    path('enable-trading', views.enable_trading, name='api-v3-settings-enable-trading'),
    path('disable-trading', views.disable_trading, name='api-v3-settings-disable-trading'),

    path('update-production-site', views.update_production_site, name='api-v3-settings-update-production_site'),
    path('add-iscc-trading-certificate', views.add_iscc_trading_certificate, name='api-v3-settings-add-iscc-trading-certificate'),
    path('add-2bs-trading-certificate', views.add_2bs_trading_certificate, name='api-v3-settings-add-2bs-trading-certificate'),
    path('delete-iscc-trading-certificate', views.delete_iscc_trading_certificate, name='api-v3-settings-delete-iscc-trading-certificate'),
    path('delete-2bs-trading-certificate', views.delete_2bs_trading_certificate, name='api-v3-settings-delete-2bs-trading-certificate'),
]

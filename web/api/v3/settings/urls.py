from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_settings, name='api-v3-settings-get'),
    path('add-production-site', views.add_production_site, name='api-v3-settings-add-production-site'),
    path('delete-production-site', views.delete_production_site, name='api-v3-settings-delete-production-site'),
    path('add-production-site-certificate', views.add_production_site_certificate, name='api-v3-settings-add-production-site-certificate'),
    path('delete-production-site-certificate', views.delete_production_site_certificate, name='api-v3-settings-delete-production-site-certificate'),
    path('add-production-site-matiere-premiere', views.add_production_site_mp, name='api-v3-settings-add-production-site-matiere-premiere'),
    path('delete-production-site-matiere-premiere', views.delete_production_site_mp, name='api-v3-settings-delete-production-site-matiere-premiere'),
    path('add-production-site-biocarburant', views.add_production_site_bc, name='api-v3-settings-add-production-site-biocarburant'),
    path('delete-production-site-biocarburant', views.delete_production_site_bc, name='api-v3-settings-delete-production-site-biocarburant'),
    path('enable-mac', views.enable_mac, name='api-v3-settings-enable-mac'),
    path('disable-mac', views.disable_mac, name='api-v3-settings-disable-mac'),
    path('enable-trading', views.enable_trading, name='api-v3-settings-enable-trading'),
    path('disable-trading', views.disable_trading, name='api-v3-settings-disable-trading'),
]

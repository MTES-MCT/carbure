from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('matieres-premieres', views.get_matieres_premieres, name='api-v3-public-matieres-premieres'),
    path('biocarburants', views.get_biocarburants, name='api-v3-public-biocarburants'),
    path('countries', views.get_countries, name='api-v3-public-countries'),
    path('entities', views.get_entities, name='api-v3-public-get-entities'),
    path('producers', views.get_producers, name='api-v3-public-get-producers'),
    path('operators', views.get_operators, name='api-v3-public-get-operators'),
    path('traders', views.get_traders, name='api-v3-public-get-traders'),
    path('delivery-sites', views.get_delivery_sites, name='api-v3-public-get-delivery-sites'),
    path('production-sites', views.get_production_sites, name='api-v3-public-get-production-sites'),

    # POST
    path('create-delivery-site', views.create_delivery_site, name='api-v3-public-create-delivery-site'),

    # HOME STATS
    path('stats', views.get_stats, name='api-v3-public-stats')
]

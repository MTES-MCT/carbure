from django.urls import path, include

from api.v2 import shared

urlpatterns = [
    # SEP 2020: separating into 4 different folders may not have been the best idea ever given the huge overlap in terms of functionality
    # TODO: merge producers/operators/traders together but keep admin separate
    path('producers/', include('api.v2.producers.urls')),
    path('operators/', include('api.v2.operators.urls')),
    path('traders/', include('api.v2.traders.urls')),
    path('administrators/', include('api.v2.administrators.urls')),

    # misc - automplete (authenticated users)
    path('shared/get-producers-autocomplete', shared.get_producers_autocomplete, name='api-v2-producers-autocomplete'),
    path('shared/get-clients-autocomplete', shared.get_clients_autocomplete, name='api-v2-clients-autocomplete'),
    path('shared/get-depots-autocomplete', shared.get_depots_autocomplete, name='api-v2-depots-autocomplete'),
    path('shared/get-prodsites-autocomplete', shared.get_prod_site_autocomplete, name='api-v2-production-sites-autocomplete'),
    path('shared/get-mps-autocomplete', shared.get_mps_autocomplete, name='api-v2-mps-autocomplete'),
    path('shared/get-bcs-autocomplete', shared.get_biocarburants_autocomplete, name='api-v2-biocarburants-autocomplete'),
    path('shared/get-ges', shared.get_ges, name='api-v2-get-ges'),
]

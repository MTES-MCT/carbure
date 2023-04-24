from django.urls import path
from .feedstocks import get_feedstocks
from .biofuels import get_biofuels
from .countries import get_countries
from .depots import get_depots
from .production_sites import get_production_sites
from .entities import get_entities
from .producers import get_producers
from .operators import get_operators
from .traders import get_traders
from .certificates import get_certificates

# from .airlines import get_airlines

urlpatterns = [
    path("feedstocks", get_feedstocks, name="resources-feedstocks"),
    path("biofuels", get_biofuels, name="resources-biofuels"),
    path("countries", get_countries, name="resources-countries"),
    path("depots", get_depots, name="resources-depots"),
    path("production-sites", get_production_sites, name="resources-production-sites"),
    path("entities", get_entities, name="resources-entities"),
    path("producers", get_producers, name="resources-producers"),
    path("operators", get_operators, name="resources-operators"),
    path("traders", get_traders, name="resources-traders"),  # TODO jamais utilisé en front. On supprime ?
    path("certificates", get_certificates, name="resources-certificates"),
    # path("airlines", get_airlines, name="resources-airlines"), # TODO ?
]

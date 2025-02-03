from django.urls import path

from resources.views import (
    get_airports,
    get_biofuels,
    get_certificates,
    get_countries,
    get_depots,
    get_entities,
    get_feedstocks,
    get_production_sites,
)

# from .airlines import get_airlines

urlpatterns = [
    path("biofuels", get_biofuels, name="resources-biofuels"),
    path("certificates", get_certificates, name="resources-certificates"),
    path("countries", get_countries, name="resources-countries"),
    path("depots", get_depots, name="resources-depots"),
    path("entities", get_entities, name="resources-entities"),
    path("feedstocks", get_feedstocks, name="resources-feedstocks"),
    path("production-sites", get_production_sites, name="resources-production-sites"),
    path("airports", get_airports, name="resources-airports"),
]

from django.urls import path

from .production_sites import get_production_sites
from .add import add_production_site
from .delete import delete_production_site
from .update import update_production_site
from .set_feedstocks import set_production_site_feedstocks
from .set_biofuels import set_production_site_biofuels
from .set_certificates import set_production_site_certificates

urlpatterns = [
    path("", get_production_sites, name="entity-production-sites"),
    path("add", add_production_site, name="entity-production-sites-add"),
    path("delete", delete_production_site, name="entity-production-sites-delete"),
    path("update", update_production_site, name="entity-production-sites-update"),
    path("set-feedstocks", set_production_site_feedstocks, name="entity-production-sites-set-feedstocks"),
    path("set-biofuels", set_production_site_biofuels, name="entity-production-sites-set-biofuels"),
    path("set-certificates", set_production_site_certificates, name="entity-production-sites-set-certificates"),
]

from traceability.models import Material
from transactions.models import Site


def material(_entity):
    return Material.objects.filter(code__startswith="H2-")


def site(entity):
    return Site.objects.filter(site_type=Site.H2_REFUELING_STATION, created_by=entity)

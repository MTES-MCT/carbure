from traceability.handlers.action import ActionIndustryLookups
from traceability.models import Material
from transactions.models import Site


class H2ActionLookups(ActionIndustryLookups):
    def material(self, _entity):
        return Material.objects.filter(code__startswith="H2-")

    def site(self, _entity):
        return Site.objects.filter(site_type=Site.H2_REFUELING_STATION)

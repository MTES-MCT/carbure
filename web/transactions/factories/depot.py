from factory import fuzzy

from transactions.factories.site import SiteFactory
from transactions.models.depot import Depot


class DepotFactory(SiteFactory):
    class Meta:
        model = Depot

    site_type = fuzzy.FuzzyChoice(Depot.DEPOT_TYPES, getter=lambda x: x[0])

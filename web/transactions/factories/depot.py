from transactions.factories.site import SiteFactory
from transactions.models.depot import Depot


class DepotFactory(SiteFactory):
    class Meta:
        model = Depot

    site_type = Depot.BIOFUELDEPOT

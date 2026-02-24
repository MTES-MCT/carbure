import factory

from transactions.factories.site import SiteFactory
from transactions.models.depot import Depot


class DepotFactory(SiteFactory):
    """Factory for Depot model with depot-specific fields."""

    class Meta:
        model = Depot

    site_type = Depot.BIOFUELDEPOT
    customs_id = factory.Faker("lexify", text="????????????")
    accise = factory.Faker("lexify", text="????????????")
    electrical_efficiency = None
    thermal_efficiency = None
    useful_temperature = None

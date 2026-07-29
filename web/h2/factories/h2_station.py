import factory
from factory import fuzzy

from core.models import Entity
from entity.factories.entity import EntityFactory
from h2.models import H2Station
from transactions.factories.site import SiteFactory
from transactions.models.site import Site


class H2StationFactory(SiteFactory):
    class Meta:
        model = H2Station

    site_type = Site.H2_REFUELING_STATION
    created_by = factory.SubFactory(EntityFactory, entity_type=Entity.HRS)

    access_type = fuzzy.FuzzyChoice(H2Station.ACCESS_TYPES, getter=lambda x: x[0])
    distributed_pressure = factory.LazyFunction(lambda: [H2Station.DP_350_BAR])
    has_personal_vehicle_connector = False
    storage_capacity = factory.Faker("random_int", min=100, max=10000)
    distribution_capacity = factory.Faker("random_int", min=50, max=5000)

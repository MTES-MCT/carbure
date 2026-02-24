import factory

from transactions.factories.site import SiteFactory
from transactions.models.airport import Airport


class AirportFactory(SiteFactory):
    """Factory for Airport model with airport-specific fields."""

    class Meta:
        model = Airport

    site_type = Airport.AIRPORT
    icao_code = factory.Faker("lexify", text="????")
    is_ue_airport = False

import factory
from factory import fuzzy

from saf.models.saf_logistics import SafLogistics
from transactions.models.airport import Airport
from transactions.models.depot import Depot


class SafLogisticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SafLogistics

    origin_depot = factory.Iterator(Depot.objects.all())
    destination_airport = factory.Iterator(Airport.objects.all())
    has_intermediary_depot = factory.Faker("boolean")
    shipping_method = fuzzy.FuzzyChoice(SafLogistics.SHIPPING_METHODS, getter=lambda c: c[0])

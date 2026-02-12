import factory
from factory import fuzzy

from core.models import Pays
from entity.factories.entity import EntityFactory
from transactions.models.site import Site


class SiteFactory(factory.django.DjangoModelFactory):
    """Base factory for Site model with common fields only."""

    class Meta:
        model = Site
        abstract = True  # Site is used via child models

    name = factory.Faker("company")
    site_siret = factory.Faker("lexify", text="????????????")
    site_type = fuzzy.FuzzyChoice(Site.SITE_TYPE, getter=lambda x: x[0])
    address = factory.Faker("address")
    postal_code = factory.Faker("postcode")
    city = factory.Faker("city")
    country = factory.Iterator(Pays.objects.all())
    gps_coordinates = ""
    private = factory.Faker("boolean")
    is_enabled = True
    created_by = factory.SubFactory(EntityFactory)

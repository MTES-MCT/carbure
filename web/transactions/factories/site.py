import factory
from factory import fuzzy

from core.models import Pays
from entity.factories.entity import EntityFactory
from transactions.models.site import Site


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site

    name = factory.Faker("company")
    site_siret = factory.Faker("lexify", text="????????????")
    customs_id = factory.Faker("lexify", text="????????????")
    icao_code = factory.Faker("lexify", text="????????????")
    site_type = fuzzy.FuzzyChoice(Site.SITE_TYPE, getter=lambda x: x[0])
    address = factory.Faker("address")
    postal_code = factory.Faker("postcode")
    city = factory.Faker("city")
    country = factory.Iterator(Pays.objects.all())
    gps_coordinates = ""
    accise = factory.Faker("lexify", text="????????????")
    electrical_efficiency = None
    thermal_efficiency = None
    useful_temperature = None
    ges_option = fuzzy.FuzzyChoice(Site.GES_OPTIONS, getter=lambda x: x[0])
    eligible_dc = factory.Faker("boolean")
    dc_number = factory.Faker("lexify", text="????????????")
    dc_reference = factory.Faker("lexify", text="????????????")
    manager_name = factory.Faker("name")
    manager_phone = factory.Faker("phone_number")
    manager_email = factory.Faker("email")
    private = factory.Faker("boolean")
    is_enabled = True
    date_mise_en_service = factory.Faker("date")
    created_by = factory.SubFactory(EntityFactory)
    is_ue_airport = False

import factory

from core.models import Pays
from transactions.models import ProductionSite


class ProductionSiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSite

    name = factory.Faker("company")
    country = factory.Iterator(Pays.objects.all())
    date_mise_en_service = factory.Faker("date_this_century", before_today=True)
    ges_option = "Default"
    eligible_dc = False
    dc_reference = ""

    address = factory.Faker("street_address")
    city = factory.Faker("city")
    postal_code = factory.Faker("postcode")
    gps_coordinates = None

    manager_name = factory.Faker("name")
    manager_phone = factory.Faker("phone_number")
    manager_email = factory.Faker("email")

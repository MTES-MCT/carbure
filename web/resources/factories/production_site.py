import factory

from producers.models import ProductionSite

from core.models import (
    CarbureStock,
    Entity,
    MatierePremiere,
    Biocarburant,
    Pays,
    Depot,
)


class ProductionSiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductionSite

    producer = factory.Iterator(Entity.objects.filter(entity_type=Entity.PRODUCER))
    name = factory.Faker("company")
    country = factory.Iterator(Pays.objects.all())
    date_mise_en_service = factory.Faker("date_this_century", before_today=True)
    ges_option = "Default"
    eligible_dc = False
    dc_reference = ""

    site_id = factory.Faker("lexify", text="????????????")
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    postal_code = factory.Faker("postcode")
    gps_coordinates = None

    manager_name = factory.Faker("name")
    manager_phone = factory.Faker("phone_number")
    manager_email = factory.Faker("email")

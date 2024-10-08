import random
from datetime import datetime

import factory

from core.models import Biocarburant, Entity, MatierePremiere, Pays
from saf.models import SafTicketSource
from transactions.models import ProductionSite


class SafTicketSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SafTicketSource

    carbure_id = factory.Faker("lexify")
    created_at = factory.Faker("date_time_this_year")
    added_by = factory.Iterator(Entity.objects.all())

    year = datetime.today().year
    delivery_period = factory.LazyAttribute(lambda obj: obj.year * 100 + random.randint(1, 12))

    total_volume = factory.Faker("random_int", min=10000, max=500000)
    assigned_volume = factory.Faker("random_int", min=0, max=10000)

    feedstock = factory.Iterator(MatierePremiere.objects.all())
    biofuel = factory.Iterator(Biocarburant.objects.all())
    country_of_origin = factory.Iterator(Pays.objects.all())

    carbure_producer = factory.Iterator(Entity.objects.filter(entity_type=Entity.PRODUCER))
    unknown_producer = factory.Faker("company")

    carbure_production_site = factory.Iterator(ProductionSite.objects.all())
    unknown_production_site = factory.Faker("company")
    production_country = factory.Iterator(Pays.objects.all())
    production_site_commissioning_date = factory.Faker("date_this_century")

    eec = factory.Faker("random_number", digits=1)
    el = factory.Faker("random_number", digits=1)
    ep = factory.Faker("random_number", digits=1)
    etd = factory.Faker("random_number", digits=1)
    eu = factory.Faker("random_number", digits=1)
    esca = factory.Faker("random_number", digits=1)
    eccs = factory.Faker("random_number", digits=1)
    eccr = factory.Faker("random_number", digits=1)
    eee = factory.Faker("random_number", digits=1)
    ghg_total = factory.Faker("random_number", digits=1)
    ghg_reference = 60
    ghg_reduction = factory.Faker("random_number", digits=2)

import random
from datetime import date, datetime

import factory

from doublecount.models import DoubleCountingApplication
from transactions.models import ProductionSite


class DoubleCountingApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingApplication

    production_site = factory.Iterator(ProductionSite.objects.all())
    producer = factory.LazyAttribute(lambda obj: obj.production_site.producer)

    # producer_user = factory.Iterator(Entity.objects.filter(entity_type=Entity.PRODUCER))

    period_start = date(datetime.today().year, 1, 1)
    period_end = date(period_start.year + 1, 12, 31)

    certificate_id = factory.Faker("lexify", text="????????????")

    status = random.choice(
        (DoubleCountingApplication.PENDING, DoubleCountingApplication.ACCEPTED, DoubleCountingApplication.REJECTED)
    )

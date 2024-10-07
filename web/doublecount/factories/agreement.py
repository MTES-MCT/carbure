from datetime import date, datetime

import factory

from certificates.models import DoubleCountingRegistration
from producers.models import ProductionSite


class DoubleCountingRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingRegistration

    production_site = factory.Iterator(ProductionSite.objects.all())
    valid_from = date(datetime.today().year, 1, 1)
    valid_until = date(valid_from.year + 1, 12, 31)
    certificate_id = factory.Faker("lexify", text="????????????")

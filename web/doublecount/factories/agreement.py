from datetime import date, datetime

import factory

from certificates.models import DoubleCountingRegistration
from doublecount.factories.application import DoubleCountingApplicationFactory
from transactions.models import ProductionSite


class DoubleCountingRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingRegistration

    production_site = factory.Iterator(ProductionSite.objects.all())
    valid_from = date(datetime.today().year, 1, 1)
    valid_until = date(valid_from.year + 1, 12, 31)
    application = factory.SubFactory(
        DoubleCountingApplicationFactory,
        production_site=factory.SelfAttribute("..production_site"),
    )
    certificate_id = factory.LazyAttribute(lambda x: x.application.certificate_id)

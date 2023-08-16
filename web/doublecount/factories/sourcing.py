import factory
from datetime import datetime

from core.models import MatierePremiere, Pays
from doublecount.models import DoubleCountingApplication, DoubleCountingSourcing


class DoubleCountingSourcingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingSourcing

    dca = factory.Iterator(DoubleCountingApplication.objects.all())
    year = datetime.today().year
    feedstock = factory.Iterator(MatierePremiere.objects.all())
    origin_country = factory.Iterator(Pays.objects.all())
    supply_country = factory.Iterator(Pays.objects.all())
    transit_country = factory.Iterator(Pays.objects.all())
    metric_tonnes = factory.Faker("random_int", min=5000, max=10000)

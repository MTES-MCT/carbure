from urllib import request
import factory
from datetime import datetime

from core.models import Biocarburant, MatierePremiere, Pays
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction, DoubleCountingSourcing


class DoubleCountingProductionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingProduction

    dca = factory.Iterator(DoubleCountingApplication.objects.all())
    year = datetime.today().year
    feedstock = factory.Iterator(MatierePremiere.objects.all())
    biofuel = factory.Iterator(Biocarburant.objects.all())
    max_production_capacity = factory.Faker("random_int", min=5000, max=10000)
    estimated_production = factory.Faker("random_int", min=3000, max=max_production_capacity)
    requested_quota = factory.Faker("random_int", min=1000, max=estimated_production)
    approved_quota = requested_quota

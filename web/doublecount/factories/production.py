from datetime import datetime

import factory

from core.models import Biocarburant, MatierePremiere
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction


class DoubleCountingProductionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoubleCountingProduction

    dca = factory.Iterator(DoubleCountingApplication.objects.all())
    year = datetime.today().year
    feedstock = factory.Iterator(MatierePremiere.objects.all())
    biofuel = factory.Iterator(Biocarburant.objects.all())
    max_production_capacity = factory.Faker("random_int", min=500000, max=1000000)
    estimated_production = factory.Faker("random_int", min=3000, max=max_production_capacity)
    requested_quota = factory.Faker("random_int", min=1000, max=estimated_production)
    approved_quota = requested_quota

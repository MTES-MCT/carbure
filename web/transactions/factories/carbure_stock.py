import factory

from core.models import (
    Biocarburant,
    CarbureStock,
    Entity,
    MatierePremiere,
    Pays,
)
from transactions.models import Depot, ProductionSite


class CarbureStockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarbureStock

    parent_lot = None
    parent_transformation = None

    carbure_id = factory.Faker("lexify", text="????????????")
    depot = factory.Iterator(Depot.objects.all())
    carbure_client = factory.Iterator(Entity.objects.all())
    remaining_volume = factory.Faker("random_int", min=5000, max=10000)
    remaining_weight = factory.Faker("random_int", min=5000, max=10000)
    remaining_lhv_amount = factory.Faker("random_int", min=5000, max=10000)
    feedstock = factory.Iterator(MatierePremiere.objects.all())
    biofuel = factory.Iterator(Biocarburant.objects.all())
    country_of_origin = factory.Iterator(Pays.objects.all())
    carbure_production_site = factory.Iterator(ProductionSite.objects.all())
    unknown_production_site = factory.Faker("company")
    production_country = factory.Iterator(Pays.objects.all())
    carbure_supplier = factory.Iterator(Entity.objects.all())
    unknown_supplier = factory.Faker("company")
    ghg_reduction = factory.Faker("random_number", digits=2)
    ghg_reduction_red_ii = factory.Faker("random_number", digits=1)

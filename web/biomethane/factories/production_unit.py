import random

import factory

from biomethane.models import BiomethaneDigestateStorage, BiomethaneProductionUnit
from core.models import Department, Entity, Pays
from entity.factories.entity import EntityFactory


class BiomethaneProductionUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneProductionUnit
        django_get_or_create = ("producer",)

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    # Site fields
    name = factory.Faker("company")
    site_siret = "12345678901234"
    address = factory.Faker("address")
    city = factory.Faker("city")
    postal_code = factory.Faker("postcode")
    country = factory.LazyFunction(lambda: Pays.objects.filter(code_pays="FR").first())
    site_type = "PRODUCTION BIOGAZ"
    # BiomethaneProductionUnit specific fields
    unit_type = BiomethaneProductionUnit.AGRICULTURAL_AUTONOMOUS
    icpe_regime = BiomethaneProductionUnit.AUTHORIZATION
    process_type = BiomethaneProductionUnit.LIQUID_PROCESS
    methanization_process = BiomethaneProductionUnit.CONTINUOUS_INFINITELY_MIXED
    production_efficiency = 85.0
    digestate_valorization_methods = [BiomethaneProductionUnit.SPREADING]


class BiomethaneDigestateStorageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneDigestateStorage

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    type = factory.LazyAttribute(lambda obj: random.choice(["Béton", "Cuve"]))
    capacity = factory.Faker("random_int", min=1000, max=10000)


def create_production_unit(producer: Entity, **kwargs):
    department, _ = Department.objects.get_or_create(code_dept="75", defaults={"name": "Paris"})
    defaults = {
        "department": department,
        "insee_code": "75101",
        "icpe_number": "75-0001",
        "spreading_management_methods": [BiomethaneProductionUnit.DIRECT_SPREADING],
        "digestate_sale_types": [BiomethaneProductionUnit.SPREADING_PLAN_ICPE],
    }
    defaults.update(kwargs)
    BiomethaneProductionUnitFactory.create(producer=producer, **defaults)

    BiomethaneDigestateStorage.objects.update_or_create(
        producer=producer,
        type="Béton",
        defaults={"capacity": 5000},
    )
    BiomethaneDigestateStorage.objects.update_or_create(
        producer=producer,
        type="Cuve",
        defaults={"capacity": 7500},
    )

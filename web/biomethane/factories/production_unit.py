import random

import factory

from biomethane.models import BiomethaneDigestateStorage, BiomethaneProductionUnit
from core.models import Entity
from entity.factories.entity import EntityFactory


class BiomethaneProductionUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneProductionUnit

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    unit_name = factory.Faker("company")
    siret_number = "12345678901234"
    company_address = factory.Faker("address")
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
    BiomethaneProductionUnitFactory.create(producer=producer, **kwargs)
    BiomethaneDigestateStorageFactory.create_batch(2, producer=producer)

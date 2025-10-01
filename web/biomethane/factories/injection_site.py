import random

import factory
from faker import Faker

from biomethane.models import BiomethaneInjectionSite
from core.models import Entity
from entity.factories.entity import EntityFactory

faker = Faker()


class BiomethaneInjectionSiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneInjectionSite

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)

    unique_identification_number = factory.Faker("lexify", text="?????")
    is_shared_injection_site = factory.Faker("boolean")
    meter_number = factory.LazyAttribute(
        lambda obj: faker.lexify(text="?????") if obj.is_different_from_production_site else None
    )
    is_different_from_production_site = factory.Faker("boolean")
    company_address = factory.LazyAttribute(lambda obj: faker.address() if obj.is_different_from_production_site else None)
    city = factory.LazyAttribute(lambda obj: faker.city() if obj.is_different_from_production_site else None)

    postal_code = factory.LazyAttribute(lambda obj: faker.postcode() if obj.is_different_from_production_site else None)

    network_type = factory.LazyAttribute(
        lambda obj: random.choice([choice[0] for choice in BiomethaneInjectionSite.NETWORK_TYPE_CHOICES])
    )
    network_manager_name = factory.Faker("company")


def create_injection_site(entity):
    BiomethaneInjectionSiteFactory.create(producer=entity)

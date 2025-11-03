import random

import factory
from faker import Faker

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity
from entity.factories.entity import EntityFactory

fake = Faker()


class BiomethaneDigestateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneDigestate

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    year = factory.LazyFunction(BiomethaneAnnualDeclarationService.get_declaration_period)

    # Production de digestat
    raw_digestate_tonnage_produced = factory.Faker("random_number", digits=4)
    raw_digestate_dry_matter_rate = factory.Faker("pyfloat", min_value=5.0, max_value=15.0, right_digits=2)
    solid_digestate_tonnage = factory.Faker("random_number", digits=4)
    liquid_digestate_quantity = factory.Faker("random_number", digits=4)

    # Épandage
    average_spreading_valorization_distance = factory.Faker("random_int", min=10, max=100)

    # Compostage (par défaut pas de compostage)
    composting_locations = []
    external_platform_name = None
    external_platform_digestate_volume = None
    external_platform_department = None
    external_platform_municipality = None
    on_site_composted_digestate_volume = None

    # Incinération/Enfouissement (par défaut pas d'incinération)
    annual_eliminated_volume = None
    incinerator_landfill_center_name = None
    wwtp_materials_to_incineration = None

    acquiring_companies = None
    sold_volume = None


def create_digestate_with_composting(producer: Entity, **kwargs):
    """Factory helper pour créer un digestat avec compostage."""
    return BiomethaneDigestateFactory.create(
        producer=producer,
        composting_locations=[BiomethaneDigestate.ON_SITE, BiomethaneDigestate.EXTERNAL_PLATFORM],
        external_platform_name=fake.company(),
        external_platform_digestate_volume=fake.random_number(digits=3),
        external_platform_department="75",
        external_platform_municipality="Paris",
        on_site_composted_digestate_volume=fake.random_number(digits=3),
        **kwargs,
    )


def create_digestate_with_incineration(producer: Entity, **kwargs):
    """Factory helper pour créer un digestat avec incinération."""
    return BiomethaneDigestateFactory.create(
        producer=producer,
        annual_eliminated_volume=fake.random_number(digits=3),
        incinerator_landfill_center_name=fake.company(),
        wwtp_materials_to_incineration=fake.random_number(digits=2),
        **kwargs,
    )


def create_digestate_with_sale(producer: Entity, **kwargs):
    """Factory helper pour créer un digestat avec vente."""
    return BiomethaneDigestateFactory.create(
        producer=producer,
        annual_sold_volume=fake.random_number(digits=3),
        sale_market=random.choice([choice[0] for choice in BiomethaneDigestate.SALE_MARKET_CHOICES]),
        **kwargs,
    )

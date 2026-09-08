from datetime import datetime

import factory
from factory import fuzzy
from faker import Faker

from biomethane.models import BiomethaneSupplyInput, BiomethaneSupplyPlan
from core.models import Entity, MatierePremiere, Pays
from entity.factories.entity import EntityFactory

faker = Faker()


class BiomethaneSupplyPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneSupplyPlan
        django_get_or_create = ("producer", "year")

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    year = factory.Faker("random_int", min=2020, max=datetime.today().year)


class BiomethaneSupplyInputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneSupplyInput

    supply_plan = factory.SubFactory(BiomethaneSupplyPlanFactory)

    # Section Intrant
    feedstock = factory.LazyFunction(lambda: MatierePremiere.biomethane.order_by("?").first())
    material_unit = fuzzy.FuzzyChoice(BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES, getter=lambda x: x[0])

    dry_matter_ratio_percent = factory.LazyAttribute(
        lambda obj: faker.random_int(min=10, max=90) if obj.material_unit == BiomethaneSupplyInput.DRY else None
    )

    # Volume
    volume = factory.Faker("random_int", min=100, max=10000)

    # Section Réception
    origin_country = factory.LazyFunction(lambda: Pays.objects.order_by("?").first())
    origin_department = factory.Faker("random_int", min=10, max=95)
    average_weighted_distance_km = factory.Faker("random_int", min=10, max=500)
    maximum_distance_km = factory.Faker("random_int", min=50, max=1000)


def create_supply_plan(entity):
    current_year = datetime.today().year
    create_supply_plan_for_year(entity, current_year - 1)
    create_supply_plan_for_year(entity, current_year)


def create_supply_plan_for_year(entity, year):
    supply_plan = BiomethaneSupplyPlanFactory.create(producer=entity, year=year)

    for origin_department in range(10, 20):
        origin_department = str(origin_department)
        if not BiomethaneSupplyInput.objects.filter(
            supply_plan=supply_plan,
            origin_department=origin_department,
        ).exists():
            BiomethaneSupplyInputFactory.create(
                supply_plan=supply_plan,
                origin_department=origin_department,
            )

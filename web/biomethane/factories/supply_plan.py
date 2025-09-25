import factory
from factory import fuzzy
from faker import Faker

from biomethane.models import BiomethaneSupplyInput, BiomethaneSupplyPlan
from core.models import Entity, Pays
from entity.factories.entity import EntityFactory

faker = Faker()


class BiomethaneSupplyPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneSupplyPlan

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    year = factory.Faker("random_int", min=2020, max=2030)


class BiomethaneSupplyInputFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneSupplyInput

    supply_plan = factory.SubFactory(BiomethaneSupplyPlanFactory)

    # Section Intrant
    source = fuzzy.FuzzyChoice(BiomethaneSupplyInput.SOURCE_CHOICES, getter=lambda x: x[0])
    crop_type = fuzzy.FuzzyChoice(BiomethaneSupplyInput.CROP_TYPE_CHOICES, getter=lambda x: x[0])
    input_category = fuzzy.FuzzyChoice(BiomethaneSupplyInput.INPUT_CATEGORY_CHOICES, getter=lambda x: x[0])
    input_type = factory.Faker("word")
    material_unit = fuzzy.FuzzyChoice(BiomethaneSupplyInput.MATERIAL_UNIT_CHOICES, getter=lambda x: x[0])

    dry_matter_ratio_percent = factory.LazyAttribute(
        lambda obj: faker.random_int(min=10, max=90) if obj.material_unit == BiomethaneSupplyInput.DRY else None
    )

    # Volume
    volume = factory.Faker("random_int", min=100, max=10000)

    # Section Réception
    origin_country = factory.Iterator(Pays.objects.all())
    origin_department = factory.Faker("lexify", text="??")
    average_weighted_distance_km = factory.Faker("random_int", min=10, max=500)
    maximum_distance_km = factory.Faker("random_int", min=50, max=1000)


def create_supply_plan(entity):
    supply_plan = BiomethaneSupplyPlanFactory.create(producer=entity)
    BiomethaneSupplyInputFactory.create_batch(10, supply_plan=supply_plan)

import factory

from traceability.models.material import Material


class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    code = factory.Faker("lexify", text="MAT-????")
    name = factory.LazyAttribute(lambda obj: f"Matière {obj.code}")

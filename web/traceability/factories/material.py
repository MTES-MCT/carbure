import factory

from traceability.models.material import Material


class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    code = factory.Sequence(lambda n: f"MAT{n:04d}")
    name = factory.LazyAttribute(lambda obj: f"Matière {obj.code}")

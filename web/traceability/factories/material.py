import factory
from factory import fuzzy

from traceability.models.material import Material
from traceability.models.material_tag import MaterialTag


class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material
        django_get_or_create = ("code",)

    code = factory.Faker("lexify", text="MAT-????")
    name = factory.LazyAttribute(lambda obj: f"Matière {obj.code}")
    unit = Material.KG
    lhv = fuzzy.FuzzyInteger(2, 100)
    density = fuzzy.FuzzyInteger(2, 100)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Create tags from (type, value) pairs when the material is saved."""
        if create and extracted:
            MaterialTag.objects.bulk_create(
                [MaterialTag(material=self, type=tag_type, value=value) for tag_type, value in extracted]
            )

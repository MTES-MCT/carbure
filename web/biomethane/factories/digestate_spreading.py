import factory
from faker import Faker

from biomethane.factories.digestate import BiomethaneDigestateFactory
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading

fake = Faker()


class BiomethaneDigestateSpreadingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneDigestateSpreading

    digestate = factory.SubFactory(BiomethaneDigestateFactory)
    spreading_department = factory.Faker("lexify", text="??")  # Code département sur 2 caractères
    spread_quantity = factory.Faker("pyfloat", min_value=10.0, max_value=1000.0, right_digits=2)
    spread_parcels_area = factory.Faker("pyfloat", min_value=5.0, max_value=500.0, right_digits=2)


def create_spreading_for_digestate(digestate, **kwargs):
    """Factory helper pour créer un spreading pour un digestat existant."""
    return BiomethaneDigestateSpreadingFactory.create(digestate=digestate, **kwargs)

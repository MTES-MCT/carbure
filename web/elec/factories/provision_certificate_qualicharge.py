from datetime import datetime

import factory

from core.models import Entity
from elec.models import ElecProvisionCertificateQualicharge


class ElecProvisionCertificateQualichargeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ElecProvisionCertificateQualicharge

    cpo = factory.LazyFunction(lambda: Entity.objects.filter(entity_type=Entity.CPO).first())
    date_from = factory.Iterator(["2025-01-01", "2025-02-01"])
    date_to = factory.Iterator(["2025-02-01", "2025-03-01"])
    year = datetime.today().year
    operating_unit = factory.LazyAttribute(lambda o: o.operating_unit_.upper())
    station_id = factory.LazyAttribute(lambda o: f"{o.operating_unit_.upper()}{o.station_id_}")
    energy_amount = factory.Faker("pyfloat", positive=True, right_digits=2, min_value=100, max_value=1000)
    is_controlled_by_qualicharge = factory.Faker("boolean")
    validated_by = factory.Iterator(ElecProvisionCertificateQualicharge.VALIDATION_CHOICES, getter=lambda c: c[0])
    created_at = datetime.now()

    class Params:
        operating_unit_ = factory.Faker("pystr", min_chars=3, max_chars=4, prefix="FR")
        station_id_ = factory.Faker("random_number", digits=4)

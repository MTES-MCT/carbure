import datetime

import factory
from factory import fuzzy

from core.models import Entity
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from entity.factories import EntityFactory


class ElecTransferCertificateFactory(factory.django.DjangoModelFactory):
    """Factory for creating elec transfer certificates."""

    class Meta:
        model = ElecTransferCertificate

    status = ElecTransferCertificate.ACCEPTED
    supplier = factory.SubFactory(EntityFactory, entity_type=Entity.CPO)
    client = factory.SubFactory(EntityFactory, entity_type=Entity.OPERATOR)
    transfer_date = factory.LazyFunction(lambda: datetime.date(2025, 1, 1))
    energy_amount = fuzzy.FuzzyFloat(10.0, 200.0)
    used_in_tiruert = False
    comment = ""

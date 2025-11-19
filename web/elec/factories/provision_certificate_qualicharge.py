import datetime

import factory
from faker import Faker

from core.models import Entity
from elec.models import ElecProvisionCertificateQualicharge

fake = Faker("fr_FR")


class ElecProvisionCertificateQualichargeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ElecProvisionCertificateQualicharge

    cpo = factory.LazyFunction(lambda: Entity.objects.filter(entity_type=Entity.CPO).first())
    unknown_siren = None
    date_from = factory.LazyFunction(lambda: datetime.date(2023, 1, 1))
    date_to = factory.LazyFunction(lambda: datetime.date(2023, 3, 31))
    year = 2023
    operating_unit = factory.Sequence(lambda n: f"FR{n:03d}")
    station_id = factory.Sequence(lambda n: f"FRXYZP{n:06d}")
    energy_amount = factory.Faker("pyfloat", positive=True, right_digits=2, min_value=100, max_value=10000)
    is_controlled_by_qualicharge = factory.Faker("boolean", chance_of_getting_true=80)
    validated_by = ElecProvisionCertificateQualicharge.NO_ONE

    class Params:
        # Parameter to create a certificate without CPO (with unknown_siren)
        without_cpo = factory.Trait(
            cpo=None,
            unknown_siren=factory.LazyAttribute(lambda o: fake.siren()),
        )

        # Parameter to create a CPO-validated certificate
        cpo_validated = factory.Trait(
            validated_by=ElecProvisionCertificateQualicharge.CPO,
        )

        # Parameter to create a DGEC-validated certificate
        dgec_validated = factory.Trait(
            validated_by=ElecProvisionCertificateQualicharge.DGEC,
        )

        # Parameter to create a double-validated certificate
        double_validated = factory.Trait(
            validated_by=ElecProvisionCertificateQualicharge.BOTH,
        )

        # Parameter to create a Q1 certificate (Jan-Mar)
        q1 = factory.Trait(
            date_from=factory.LazyFunction(lambda: datetime.date(2023, 1, 1)),
            date_to=factory.LazyFunction(lambda: datetime.date(2023, 3, 31)),
            year=2023,
        )

        # Parameter to create a Q2 certificate (Apr-Jun)
        q2 = factory.Trait(
            date_from=factory.LazyFunction(lambda: datetime.date(2023, 4, 1)),
            date_to=factory.LazyFunction(lambda: datetime.date(2023, 6, 30)),
            year=2023,
        )

        # Parameter to create a Q3 certificate (Jul-Sep)
        q3 = factory.Trait(
            date_from=factory.LazyFunction(lambda: datetime.date(2023, 7, 1)),
            date_to=factory.LazyFunction(lambda: datetime.date(2023, 9, 30)),
            year=2023,
        )

        # Parameter to create a Q4 certificate (Oct-Dec)
        q4 = factory.Trait(
            date_from=factory.LazyFunction(lambda: datetime.date(2023, 10, 1)),
            date_to=factory.LazyFunction(lambda: datetime.date(2023, 12, 31)),
            year=2023,
        )

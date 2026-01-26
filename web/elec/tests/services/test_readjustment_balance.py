from datetime import date

from django.test import TestCase

from core.models import Entity
from elec.models.elec_certificate_readjustment import ElecCertificateReadjustment
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.services.readjustment_balance import get_readjustment_balance


class ReadjustmentBalanceTest(TestCase):
    def setUp(self):
        self.cpo = Entity.objects.create(name="CPO", entity_type=Entity.CPO, has_elec=True)
        self.other_cpo = Entity.objects.create(name="OTHER", entity_type=Entity.CPO, has_elec=True)
        self.operator = Entity.objects.create(name="OPERATOR", entity_type=Entity.OPERATOR, has_elec=True)

    def test_returns_zero_without_readjustments(self):
        assert get_readjustment_balance(self.cpo) == 0

    def test_computes_difference_between_expected_and_confirmed(self):
        ElecCertificateReadjustment.objects.create(
            cpo=self.cpo,
            energy_amount=100,
            error_source=ElecCertificateReadjustment.METER_READINGS,
        )
        ElecCertificateReadjustment.objects.create(
            cpo=self.cpo,
            energy_amount=40,
            error_source=ElecCertificateReadjustment.MANUAL,
        )
        # Should be ignored (different supplier)
        ElecCertificateReadjustment.objects.create(
            cpo=self.other_cpo,
            energy_amount=500,
            error_source=ElecCertificateReadjustment.METER_READINGS,
        )

        ElecTransferCertificate.objects.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=60,
            transfer_date=date.today(),
            is_readjustment=True,
            status=ElecTransferCertificate.ACCEPTED,
        )
        # Should be ignored (not flagged as readjustment)
        ElecTransferCertificate.objects.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=10,
            transfer_date=date.today(),
            is_readjustment=False,
            status=ElecTransferCertificate.ACCEPTED,
        )
        # Should be ignored (different supplier)
        ElecTransferCertificate.objects.create(
            supplier=self.other_cpo,
            client=self.operator,
            energy_amount=15,
            transfer_date=date.today(),
            is_readjustment=True,
            status=ElecTransferCertificate.ACCEPTED,
        )

        assert get_readjustment_balance(self.cpo) == 80

    def test_returns_zero_when_expected_and_confirmed_match(self):
        ElecCertificateReadjustment.objects.create(
            cpo=self.cpo,
            energy_amount=50,
            error_source=ElecCertificateReadjustment.METER_READINGS,
        )
        ElecTransferCertificate.objects.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=50,
            transfer_date=date.today(),
            is_readjustment=True,
            status=ElecTransferCertificate.ACCEPTED,
        )

        assert get_readjustment_balance(self.cpo) == 0

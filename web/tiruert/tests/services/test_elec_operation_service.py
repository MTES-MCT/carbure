from datetime import date

from django.test import TestCase
from rest_framework import serializers

from core.models import Entity
from elec.factories import ElecTransferCertificateFactory
from elec.models import ElecTransferCertificate
from tiruert.factories import ElecOperationFactory
from tiruert.models import ElecOperation
from tiruert.services.elec_operation import ElecOperationService


class ElecOperationServiceUpdateCPOTest(TestCase):
    def setUp(self):
        self.operator = Entity.objects.create(name="Operator", entity_type=Entity.OPERATOR, has_elec=True)
        self.cpo = Entity.objects.create(name="CPO", entity_type=Entity.CPO, has_elec=True)

    def test_creates_operation_when_diff_positive(self):
        ElecTransferCertificateFactory.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=10,  # MWh
            transfer_date=date(2025, 1, 15),
        )
        ElecTransferCertificateFactory.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=5,
            transfer_date=date(2025, 2, 1),
            used_in_tiruert=True,  # should be ignored
        )
        ElecOperationFactory.create(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.ACCEPTED,
            quantity=1_000,  # MJ already generated
            credited_entity=self.operator,
        )

        result = ElecOperationService.update_operator_cpo_acquisition_operations(self.operator)

        self.assertIsInstance(result, ElecOperation)
        self.assertEqual(result.quantity, (10 * 3600) - 1_000)
        self.assertEqual(result.type, ElecOperation.ACQUISITION_FROM_CPO)
        self.assertEqual(result.status, ElecOperation.ACCEPTED)
        self.assertEqual(result.credited_entity, self.operator)

    def test_returns_none_when_diff_zero(self):
        ElecTransferCertificateFactory.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=7,
            transfer_date=date(2025, 3, 10),
        )
        ElecOperationFactory.create(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.ACCEPTED,
            quantity=7 * 3600,
            credited_entity=self.operator,
        )

        result = ElecOperationService.update_operator_cpo_acquisition_operations(self.operator)

        self.assertIsNone(result)
        self.assertEqual(
            ElecOperation.objects.filter(type=ElecOperation.ACQUISITION_FROM_CPO, credited_entity=self.operator).count(),
            1,
        )

    def test_raises_when_diff_negative(self):
        ElecTransferCertificateFactory.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=5,
            transfer_date=date(2025, 4, 5),
        )
        ElecOperationFactory.create(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.ACCEPTED,
            quantity=20_000,
            credited_entity=self.operator,
        )

        with self.assertRaises(Exception):
            ElecOperationService.update_operator_cpo_acquisition_operations(self.operator)

    def test_ignores_certificates_not_matching_filters(self):
        other_supplier = Entity.objects.create(name="Not a CPO", entity_type=Entity.OPERATOR, has_elec=True)
        ElecTransferCertificateFactory.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=50,
            transfer_date=date(2024, 12, 31),  # filtered out by year
        )
        ElecTransferCertificateFactory.create(
            supplier=other_supplier,
            client=self.operator,
            energy_amount=60,
            transfer_date=date(2025, 1, 10),
            status=ElecTransferCertificate.PENDING,
        )

        result = ElecOperationService.update_operator_cpo_acquisition_operations(self.operator)

        self.assertIsNone(result)
        self.assertFalse(
            ElecOperation.objects.filter(type=ElecOperation.ACQUISITION_FROM_CPO, credited_entity=self.operator).exists()
        )

    def test_handles_empty_aggregates(self):
        other_operator = Entity.objects.create(name="No data operator", entity_type=Entity.OPERATOR, has_elec=True)

        result = ElecOperationService.update_operator_cpo_acquisition_operations(other_operator)

        self.assertIsNone(result)

    def test_existing_operations_not_accepted_do_not_reduce_diff(self):
        ElecTransferCertificateFactory.create(
            supplier=self.cpo,
            client=self.operator,
            energy_amount=5,
            transfer_date=date(2025, 5, 1),
        )
        ElecOperationFactory.create(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.PENDING,  # should be ignored in aggregate
            quantity=5 * 3600,
            credited_entity=self.operator,
        )

        result = ElecOperationService.update_operator_cpo_acquisition_operations(self.operator)

        self.assertIsNotNone(result)
        self.assertEqual(result.quantity, 5 * 3600)


class ElecOperationServiceChecksTest(TestCase):
    def setUp(self):
        self.operator = Entity.objects.create(name="Operator with balance", entity_type=Entity.OPERATOR, has_elec=True)
        counterparty = Entity.objects.create(name="Counterparty", entity_type=Entity.CPO, has_elec=True)

        self.credit = ElecOperationFactory.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=150,
            credited_entity=self.operator,
            debited_entity=counterparty,
        )
        self.debit = ElecOperationFactory.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=50,
            debited_entity=self.operator,
            credited_entity=counterparty,
        )

    def test_skips_when_no_debited_entity(self):
        ElecOperationService.perform_checks_before_create(None, {"quantity": 100, "debited_entity": None})

    def test_raises_when_quantity_exceeds_available(self):
        with self.assertRaises(serializers.ValidationError):
            ElecOperationService.perform_checks_before_create(
                None,
                {"quantity": 120, "debited_entity": self.operator},
            )

    def test_allows_when_quantity_within_available(self):
        ElecOperationService.perform_checks_before_create(
            None,
            {"quantity": 80, "debited_entity": self.operator},
        )

    def test_adds_updated_quantity_to_available(self):
        ElecOperationService.perform_checks_before_create(
            None,
            {"quantity": 120, "debited_entity": self.operator},
            updated=self.debit,
        )

    def test_raises_when_no_available_balance(self):
        new_operator = Entity.objects.create(name="Empty operator", entity_type=Entity.OPERATOR, has_elec=True)

        with self.assertRaises(serializers.ValidationError):
            ElecOperationService.perform_checks_before_create(
                None,
                {"quantity": 10, "debited_entity": new_operator},
            )

    def test_raises_when_update_still_exceeds_available(self):
        with self.assertRaises(serializers.ValidationError):
            ElecOperationService.perform_checks_before_create(
                None,
                {"quantity": 160, "debited_entity": self.operator},
                updated=self.debit,
            )

    def test_pending_operations_are_counted_in_available_balance(self):
        counterparty = Entity.objects.create(name="Pending counterparty", entity_type=Entity.CPO, has_elec=True)
        ElecOperationFactory.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.PENDING,
            quantity=40,
            debited_entity=self.operator,
            credited_entity=counterparty,
        )

        with self.assertRaises(serializers.ValidationError):
            ElecOperationService.perform_checks_before_create(
                None,
                {"quantity": 120, "debited_entity": self.operator},
            )

    def test_operations_from_other_entities_do_not_affect_available_balance(self):
        other = Entity.objects.create(name="Other operator", entity_type=Entity.OPERATOR, has_elec=True)
        ElecOperationFactory.create(
            type=ElecOperation.CESSION,
            status=ElecOperation.ACCEPTED,
            quantity=1_000,
            credited_entity=other,
        )

        with self.assertRaises(serializers.ValidationError):
            ElecOperationService.perform_checks_before_create(
                None,
                {"quantity": 120, "debited_entity": self.operator},
            )

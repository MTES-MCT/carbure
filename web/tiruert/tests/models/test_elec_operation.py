from django.test import TestCase

from core.models import Entity
from tiruert.models.elec_operation import ElecOperation


class ElecOperationAvoidedEmissionsTest(TestCase):
    """Tests for ElecOperation.avoided_emissions property."""

    def test_avoided_emissions_converts_mj_to_tco2(self):
        """Should apply EMISSION_RATE_PER_MJ and convert to tCO2."""
        operation = ElecOperation(quantity=10_000)  # MJ

        result = operation.avoided_emissions

        expected = ElecOperation.EMISSION_RATE_PER_MJ * 10_000 / 1e6
        self.assertAlmostEqual(result, expected)


class ElecOperationIsAcquisitionTest(TestCase):
    """Tests for ElecOperation.is_acquisition(entity_id)."""

    def setUp(self):
        self.entity = Entity.objects.create(name="Credited", entity_type=Entity.OPERATOR)
        self.other_entity = Entity.objects.create(name="Other", entity_type=Entity.OPERATOR)

    def test_returns_false_when_no_credited_entity(self):
        """Should be False when credited_entity is None."""
        operation = ElecOperation(type=ElecOperation.CESSION, credited_entity=None)

        self.assertFalse(operation.is_acquisition(self.entity.id))

    def test_returns_true_when_credited_entity_matches_and_type_cession(self):
        """Should be True only for CESSION credited to the given entity."""
        operation = ElecOperation(type=ElecOperation.CESSION, credited_entity=self.entity)

        self.assertTrue(operation.is_acquisition(self.entity.id))

    def test_returns_false_when_type_not_cession_even_if_entity_matches(self):
        """Should be False for non-CESSION types even with matching credited entity."""
        operation = ElecOperation(type=ElecOperation.ACQUISITION_FROM_CPO, credited_entity=self.entity)

        self.assertFalse(operation.is_acquisition(self.entity.id))

    def test_returns_false_when_credited_entity_does_not_match(self):
        """Should be False when credited_entity differs from provided entity_id."""
        operation = ElecOperation(type=ElecOperation.CESSION, credited_entity=self.other_entity)

        self.assertFalse(operation.is_acquisition(self.entity.id))


class ElecOperationIsCreditTest(TestCase):
    """Tests for ElecOperation.is_credit(entity_id)."""

    def setUp(self):
        self.entity = Entity.objects.create(name="Credited", entity_type=Entity.OPERATOR)
        self.other_entity = Entity.objects.create(name="Other", entity_type=Entity.OPERATOR)

    def test_returns_false_when_no_credited_entity(self):
        """Should be False when credited_entity is None."""
        operation = ElecOperation(credited_entity=None)

        self.assertFalse(operation.is_credit(self.entity.id))

    def test_returns_true_when_credited_entity_matches(self):
        """Should be True when credited_entity matches entity_id."""
        operation = ElecOperation(credited_entity=self.entity)

        self.assertTrue(operation.is_credit(self.entity.id))

    def test_returns_false_when_credited_entity_does_not_match(self):
        """Should be False when credited_entity differs from entity_id."""
        operation = ElecOperation(credited_entity=self.other_entity)

        self.assertFalse(operation.is_credit(self.entity.id))

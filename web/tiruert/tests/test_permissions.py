from django.test import TestCase

from core.models import Entity
from entity.factories import EntityFactory
from tiruert.permissions import can_access_balance_and_operations, can_access_objectives


def build_entity(**kwargs):
    kwargs.setdefault("registered_country", None)  # to avoid lazy loading of country fixtures in tests (db query)
    return EntityFactory.build(**kwargs)


class CanAccessBalanceAndOperationsTest(TestCase):
    """Tests for the can_access_balance_and_operations permission function."""

    def test_operator_with_accise_number_can_access(self):
        """OPERATOR with accise_number always has access regardless of has_mac."""
        entity = build_entity(entity_type=Entity.OPERATOR, has_mac=False, accise_number="ACC123")
        self.assertTrue(can_access_balance_and_operations(entity))

    def test_operator_without_accise_number_cannot_access(self):
        """OPERATOR without accise_number cannot access."""
        entity = build_entity(entity_type=Entity.OPERATOR, has_mac=False, accise_number="")
        self.assertFalse(can_access_balance_and_operations(entity))

    def test_producer_with_mac_and_accise_number_can_access(self):
        """PRODUCER with has_mac=True and accise_number can access."""
        entity = build_entity(entity_type=Entity.PRODUCER, has_mac=True, accise_number="ACC123")
        self.assertTrue(can_access_balance_and_operations(entity))

    def test_producer_without_mac_cannot_access(self):
        """PRODUCER with has_mac=False cannot access even with accise_number."""
        entity = build_entity(entity_type=Entity.PRODUCER, has_mac=False, accise_number="ACC123")
        self.assertFalse(can_access_balance_and_operations(entity))

    def test_producer_with_mac_but_no_accise_number_cannot_access(self):
        """PRODUCER with has_mac=True but no accise_number cannot access."""
        entity = build_entity(entity_type=Entity.PRODUCER, has_mac=True, accise_number="")
        self.assertFalse(can_access_balance_and_operations(entity))

    def test_trader_with_mac_and_accise_number_can_access(self):
        """TRADER with has_mac=True and accise_number can access."""
        entity = build_entity(entity_type=Entity.TRADER, has_mac=True, accise_number="ACC123")
        self.assertTrue(can_access_balance_and_operations(entity))

    def test_trader_without_mac_cannot_access(self):
        """TRADER with has_mac=False cannot access even with accise_number."""
        entity = build_entity(entity_type=Entity.TRADER, has_mac=False, accise_number="ACC123")
        self.assertFalse(can_access_balance_and_operations(entity))

    def test_trader_with_mac_but_no_accise_number_cannot_access(self):
        """TRADER with has_mac=True but no accise_number cannot access."""
        entity = build_entity(entity_type=Entity.TRADER, has_mac=True, accise_number="")
        self.assertFalse(can_access_balance_and_operations(entity))


class CanAccessObjectivesTest(TestCase):
    """Tests for the can_access_objectives permission function."""

    def test_operator_with_accise_and_tiruert_liable_can_access(self):
        """OPERATOR with accise_number and is_tiruert_liable can access objectives."""
        entity = build_entity(entity_type=Entity.OPERATOR, accise_number="ACC123", is_tiruert_liable=True)
        self.assertTrue(can_access_objectives(entity))

    def test_operator_without_tiruert_liable_cannot_access(self):
        """OPERATOR with accise_number but is_tiruert_liable=False cannot access objectives."""
        entity = build_entity(entity_type=Entity.OPERATOR, accise_number="ACC123", is_tiruert_liable=False)
        self.assertFalse(can_access_objectives(entity))

    def test_operator_without_accise_number_cannot_access(self):
        """OPERATOR without accise_number cannot access objectives."""
        entity = build_entity(entity_type=Entity.OPERATOR, accise_number="", is_tiruert_liable=True)
        self.assertFalse(can_access_objectives(entity))

    def test_producer_with_mac_accise_and_tiruert_liable_can_access(self):
        """PRODUCER with has_mac=True, accise_number and is_tiruert_liable can access objectives."""
        entity = build_entity(
            entity_type=Entity.PRODUCER,
            has_mac=True,
            accise_number="ACC123",
            is_tiruert_liable=True,
        )
        self.assertTrue(can_access_objectives(entity))

    def test_producer_without_mac_cannot_access(self):
        """PRODUCER with has_mac=False cannot access objectives."""
        entity = build_entity(
            entity_type=Entity.PRODUCER,
            has_mac=False,
            accise_number="ACC123",
            is_tiruert_liable=True,
        )
        self.assertFalse(can_access_objectives(entity))

    def test_producer_with_mac_but_not_tiruert_liable_cannot_access(self):
        """PRODUCER with has_mac=True but is_tiruert_liable=False cannot access objectives."""
        entity = build_entity(
            entity_type=Entity.PRODUCER,
            has_mac=True,
            accise_number="ACC123",
            is_tiruert_liable=False,
        )
        self.assertFalse(can_access_objectives(entity))

    def test_producer_with_mac_but_no_accise_number_cannot_access(self):
        """PRODUCER with has_mac=True but no accise_number cannot access objectives."""
        entity = build_entity(
            entity_type=Entity.PRODUCER,
            has_mac=True,
            accise_number="",
            is_tiruert_liable=True,
        )
        self.assertFalse(can_access_objectives(entity))

    def test_trader_with_mac_accise_and_tiruert_liable_can_access(self):
        """TRADER with has_mac=True, accise_number and is_tiruert_liable can access objectives."""
        entity = build_entity(entity_type=Entity.TRADER, has_mac=True, accise_number="ACC123", is_tiruert_liable=True)
        self.assertTrue(can_access_objectives(entity))

    def test_trader_without_mac_cannot_access(self):
        """TRADER with has_mac=False cannot access objectives."""
        entity = build_entity(entity_type=Entity.TRADER, has_mac=False, accise_number="ACC123", is_tiruert_liable=True)
        self.assertFalse(can_access_objectives(entity))

    def test_trader_with_mac_but_not_tiruert_liable_cannot_access(self):
        """TRADER with has_mac=True but is_tiruert_liable=False cannot access objectives."""
        entity = build_entity(
            entity_type=Entity.PRODUCER,
            has_mac=True,
            accise_number="ACC123",
            is_tiruert_liable=False,
        )
        self.assertFalse(can_access_objectives(entity))

    def test_trader_with_mac_but_no_accise_number_cannot_access(self):
        """TRADER with has_mac=True but no accise_number cannot access objectives."""
        entity = build_entity(
            entity_type=Entity.TRADER,
            has_mac=True,
            accise_number="",
            is_tiruert_liable=True,
        )
        self.assertFalse(can_access_objectives(entity))

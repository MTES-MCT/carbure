from unittest.mock import patch

from django.test import SimpleTestCase

from core.models import Entity, ExternalAdminRights
from h2.handlers.authorization import (
    can_hrs_transfer,
    can_liable_consume,
    can_liable_transfer,
    is_h2_admin,
    is_hrs_holder,
    is_liable_holder,
)


class ActionAuthorizationTest(SimpleTestCase):
    def test_status_assignment_requires_the_hrs_holder(self):
        hrs = Entity(id=1, entity_type=Entity.HRS)
        other_hrs = Entity(id=2, entity_type=Entity.HRS)
        operator = Entity(id=3, entity_type=Entity.OPERATOR)

        self.assertTrue(is_hrs_holder(hrs, hrs, None))
        self.assertFalse(is_hrs_holder(other_hrs, hrs, None))
        self.assertFalse(is_hrs_holder(operator, operator, None))

    def test_transfer_requires_the_holding_hrs_and_a_liable_recipient(self):
        hrs = Entity(id=1, entity_type=Entity.HRS)
        other_hrs = Entity(id=2, entity_type=Entity.HRS)
        recipient = Entity(id=3, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        other_operator = Entity(id=4, entity_type=Entity.OPERATOR, is_tiruert_liable=False)

        liable_hrs = Entity(id=5, entity_type=Entity.HRS, is_tiruert_liable=True)

        self.assertTrue(can_hrs_transfer(hrs, recipient, hrs))
        self.assertTrue(can_hrs_transfer(liable_hrs, recipient, liable_hrs))
        self.assertFalse(can_hrs_transfer(other_hrs, recipient, hrs))
        self.assertFalse(can_hrs_transfer(recipient, recipient, hrs))
        self.assertFalse(can_hrs_transfer(hrs, hrs, None))
        self.assertFalse(can_hrs_transfer(hrs, other_operator, hrs))
        self.assertFalse(can_hrs_transfer(liable_hrs, liable_hrs, liable_hrs))

    def test_a_liable_holder_can_transfer_to_another_liable_party(self):
        liable = Entity(id=1, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        recipient = Entity(id=2, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        other = Entity(id=3, entity_type=Entity.OPERATOR, is_tiruert_liable=False)

        self.assertTrue(can_liable_transfer(liable, recipient, liable))
        self.assertFalse(can_liable_transfer(liable, liable, liable))
        self.assertFalse(can_liable_transfer(liable, other, liable))
        self.assertFalse(can_liable_transfer(recipient, recipient, liable))

    def test_a_liable_holder_can_consume_their_own_volume(self):
        liable = Entity(id=1, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        other = Entity(id=2, entity_type=Entity.OPERATOR, is_tiruert_liable=True)

        self.assertTrue(can_liable_consume(liable, liable, liable))
        self.assertFalse(can_liable_consume(liable, other, liable))
        self.assertFalse(can_liable_consume(other, liable, liable))
        self.assertFalse(can_liable_consume(liable, liable, other))

    def test_status_assignment_requires_the_liable_holder(self):
        liable = Entity(id=1, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        other_liable = Entity(id=2, entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        sender = Entity(id=3, entity_type=Entity.HRS)
        not_liable = Entity(id=4, entity_type=Entity.OPERATOR, is_tiruert_liable=False)

        self.assertTrue(is_liable_holder(liable, liable, sender))
        self.assertTrue(is_liable_holder(liable, liable, None))
        self.assertFalse(is_liable_holder(other_liable, liable, sender))
        self.assertFalse(is_liable_holder(sender, liable, sender))
        self.assertFalse(is_liable_holder(not_liable, not_liable, sender))

    def test_status_assignment_requires_an_admin_or_h2_admin_right(self):
        admin = Entity(id=1, entity_type=Entity.ADMIN)
        external_admin = Entity(id=2, entity_type=Entity.EXTERNAL_ADMIN)
        operator = Entity(id=3, entity_type=Entity.OPERATOR)

        with patch.object(Entity, "has_external_admin_right", return_value=False) as has_right:
            self.assertTrue(is_h2_admin(admin, operator, None))
            has_right.assert_not_called()
            self.assertFalse(is_h2_admin(external_admin, operator, None))
            self.assertFalse(is_h2_admin(operator, operator, None))
        with patch.object(Entity, "has_external_admin_right", return_value=True) as has_right:
            self.assertTrue(is_h2_admin(external_admin, operator, None))
            has_right.assert_called_once_with(ExternalAdminRights.H2)

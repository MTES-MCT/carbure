from unittest.mock import patch

from django.test import SimpleTestCase

from core.models import Entity, ExternalAdminRights
from h2.handlers.authorization import can_create_consumption, can_create_valorization


class ActionAuthorizationTest(SimpleTestCase):
    def test_consumption_requires_an_hrs_creating_for_itself(self):
        hrs = Entity(id=1, entity_type=Entity.HRS)
        other_hrs = Entity(id=2, entity_type=Entity.HRS)
        operator = Entity(id=3, entity_type=Entity.OPERATOR)

        self.assertTrue(can_create_consumption(hrs, None, hrs))
        self.assertFalse(can_create_consumption(hrs, None, other_hrs))
        self.assertFalse(can_create_consumption(operator, None, operator))

    def test_valorization_requires_an_admin_and_an_hrs_recipient(self):
        admin = Entity(id=1, entity_type=Entity.ADMIN)
        external_admin = Entity(id=2, entity_type=Entity.EXTERNAL_ADMIN)
        hrs = Entity(id=3, entity_type=Entity.HRS)
        operator = Entity(id=4, entity_type=Entity.OPERATOR)

        with patch.object(Entity, "has_external_admin_right", return_value=True) as has_right:
            self.assertTrue(can_create_valorization(external_admin, hrs, hrs))
            has_right.assert_called_with(ExternalAdminRights.H2)
        with patch.object(Entity, "has_external_admin_right", return_value=False):
            self.assertTrue(can_create_valorization(admin, hrs, hrs))
            self.assertFalse(can_create_valorization(external_admin, hrs, hrs))
            self.assertFalse(can_create_valorization(operator, hrs, hrs))
            self.assertFalse(can_create_valorization(admin, hrs, operator))

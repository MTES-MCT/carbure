from unittest.mock import patch

from django.test import SimpleTestCase

from core.models import Entity, ExternalAdminRights
from h2.handlers.authorization import is_h2_admin, is_hrs_holder


class ActionAuthorizationTest(SimpleTestCase):
    def test_status_assignment_requires_the_hrs_holder(self):
        hrs = Entity(id=1, entity_type=Entity.HRS)
        other_hrs = Entity(id=2, entity_type=Entity.HRS)
        operator = Entity(id=3, entity_type=Entity.OPERATOR)

        self.assertTrue(is_hrs_holder(hrs, hrs, None))
        self.assertFalse(is_hrs_holder(other_hrs, hrs, None))
        self.assertFalse(is_hrs_holder(operator, operator, None))

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

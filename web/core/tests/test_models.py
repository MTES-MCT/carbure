from unittest import TestCase
from unittest.mock import patch

from core.models import Entity


class EntityTest(TestCase):
    def setUp(self):
        self.patched_UserRights = patch("core.models.UserRights").start()

    def tearDown(self):
        patch.stopall()

    def test_retrieves_its_admin_users(self):
        patched_filter = self.patched_UserRights.objects.filter
        patched_values_list = patched_filter.return_value.values_list

        entity = Entity()
        patched_filter.assert_not_called()
        patched_values_list.assert_not_called()

        entity.get_admin_users_emails()
        patched_filter.assert_called_with(entity=entity, role=self.patched_UserRights.ADMIN, user__is_active=True)
        patched_values_list.assert_called_with("user__email", flat=True)

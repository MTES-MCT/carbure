from decimal import Decimal

from django.test import TestCase

from core.tests_utils import PermissionTestMixin
from h2.handlers import H2ActionHandler
from h2.permissions import HasHRSRights, HasHRSWriteRights


class H2ActionHandlerPermissionTest(TestCase, PermissionTestMixin):
    def test_permissions(self):
        handler = H2ActionHandler()

        for action in ["list", "retrieve", "filters", "get_years", "download_import_template"]:
            with self.subTest(action=action):
                self.assertPermissionsEqual(handler.get_permissions(action), [HasHRSRights()])

        for action in ["destroy", "import_actions"]:
            with self.subTest(action=action):
                self.assertPermissionsEqual(handler.get_permissions(action), [HasHRSWriteRights()])


class H2ActionQuantityConversionTest(TestCase):
    def test_h2_handler_converts_kg_to_mj_and_back(self):
        handler = H2ActionHandler()
        kilograms = Decimal("120000.000")

        stored = handler.to_mj(kilograms, "kg")
        self.assertEqual(stored, kilograms * H2ActionHandler.MJ_PER_KG)
        self.assertEqual(handler.from_mj(stored, "kg"), kilograms)
        self.assertEqual(handler.from_mj(stored, "MJ"), stored)
        self.assertEqual(handler.excel_quantity_unit, "kg")

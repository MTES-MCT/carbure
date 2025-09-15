from django.test import TestCase

from biomethane.mixins.permissions import BiomethanePermissionsMixin
from core.models import Entity, UserRights


class BiomethanePermissionsMixinTests(TestCase):
    def setUp(self):
        self.mixin = BiomethanePermissionsMixin()

    def test_write_actions_initialization(self):
        """Test that write_actions is initialized as an empty list"""
        self.assertEqual(self.mixin.write_actions, [])

    def test_get_permissions_with_write_action(self):
        """Test that get_permissions returns the correct permission for a write action"""
        self.mixin.write_actions = ["upsert"]
        self.mixin.action = "upsert"
        permissions = self.mixin.get_permissions()
        self.assertEqual(permissions[0].role, [UserRights.ADMIN, UserRights.RW])
        self.assertEqual(permissions[0].entity_type, [Entity.BIOMETHANE_PRODUCER])

    def test_get_permissions_with_read_action(self):
        """Test that get_permissions returns the correct permission for a read action"""
        self.mixin.action = "retrieve"
        permissions = self.mixin.get_permissions()
        self.assertEqual(permissions[0].role, None)
        self.assertEqual(permissions[0].entity_type, [Entity.BIOMETHANE_PRODUCER])

from django.test import TestCase

from biomethane.permissions import get_biomethane_permissions
from core.models import Entity, UserRights


class BiomethanePermissionsMixinTests(TestCase):
    def test_write_actions_initialization(self):
        """Test that write_actions throws an error if it is not a list"""
        with self.assertRaises(ValueError):
            get_biomethane_permissions("upsert", "upsert")

    def test_get_permissions_with_write_action(self):
        """Test that get_permissions returns the correct permission for a write action"""
        permissions = get_biomethane_permissions(["upsert", "validate"], "upsert")
        self.assertEqual(permissions[0].role, [UserRights.ADMIN, UserRights.RW])
        self.assertEqual(permissions[0].entity_type, [Entity.BIOMETHANE_PRODUCER])

    def test_get_permissions_with_read_action(self):
        """Test that get_permissions returns the correct permission for a read action"""
        permissions = get_biomethane_permissions(["upsert", "validate"], "retrieve")
        self.assertEqual(permissions[0].op1.role, None)
        self.assertEqual(permissions[0].op1.entity_type, [Entity.BIOMETHANE_PRODUCER])

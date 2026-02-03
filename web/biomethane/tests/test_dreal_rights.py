from unittest.mock import Mock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from biomethane.factories import BiomethaneProductionUnitFactory
from biomethane.permissions import HasDrealRights
from core.models import Department, Entity, ExternalAdminRights
from entity.models import EntityScope


class HasDrealRightsUnitTest(TestCase):
    """Unit tests for HasDrealRights permission class"""

    def setUp(self):
        # Create departments
        self.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        self.dept_02 = Department.objects.create(code_dept="02", name="Aisne")

        # Create DREAL entity
        self.dreal = Entity.objects.create(name="DREAL Test", entity_type=Entity.EXTERNAL_ADMIN)

        # Associate DREAL entity with department 01
        dept_ct = ContentType.objects.get_for_model(Department)
        EntityScope.objects.create(entity=self.dreal, content_type=dept_ct, object_id=self.dept_01.id)

        # Create DREAL rights
        self.dreal_right = ExternalAdminRights.objects.create(entity=self.dreal, right=ExternalAdminRights.DREAL)

        # Create producers
        self.producer = Entity.objects.create(name="Producer", entity_type=Entity.BIOMETHANE_PRODUCER)
        self.producer2 = Entity.objects.create(name="Producer 2", entity_type=Entity.BIOMETHANE_PRODUCER)

        # Create production units
        self.unit_accessible = BiomethaneProductionUnitFactory.create(
            created_by=self.producer,
            name="Unit Accessible",
            department=self.dept_01,
        )

        self.unit_inaccessible = BiomethaneProductionUnitFactory.create(
            created_by=self.producer2,
            name="Unit Inaccessible",
            department=self.dept_02,
        )

        # Create mock request with DREAL entity
        self.request = Mock()
        self.request.entity = self.dreal

        # Create permission instance
        self.permission = HasDrealRights()

    def test_has_object_permission_with_accessible_department(self):
        """has_object_permission returns True when object department is accessible"""
        result = self.permission.has_object_permission(self.request, None, self.unit_accessible)
        self.assertTrue(result)

    def test_has_object_permission_with_inaccessible_department(self):
        """has_object_permission returns False when object department is not accessible"""
        result = self.permission.has_object_permission(self.request, None, self.unit_inaccessible)
        self.assertFalse(result)

    def test_has_object_permission_with_production_unit_property(self):
        """has_object_permission works with objects that have production_unit property"""
        # Create a mock object with ONLY production_unit attribute (no department)
        mock_obj = Mock(spec=["production_unit"])
        mock_obj.production_unit = self.unit_accessible

        result = self.permission.has_object_permission(self.request, None, mock_obj)
        self.assertTrue(result)

    def test_has_object_permission_with_no_department(self):
        """has_object_permission returns False when object has no department"""

        # Create a mock object with neither department nor production_unit
        mock_obj = Mock(spec=[])

        result = self.permission.has_object_permission(self.request, None, mock_obj)
        self.assertFalse(result)

    def test_has_object_permission_with_multiple_accessible_departments(self):
        """has_object_permission works with multiple accessible departments"""
        # Add second department to DREAL entity
        dept_ct = ContentType.objects.get_for_model(Department)
        EntityScope.objects.create(entity=self.dreal, content_type=dept_ct, object_id=self.dept_02.id)

        # Should now be able to access both units
        result_01 = self.permission.has_object_permission(self.request, None, self.unit_accessible)
        result_02 = self.permission.has_object_permission(self.request, None, self.unit_inaccessible)

        self.assertTrue(result_01)
        self.assertTrue(result_02)

    def test_has_object_permission_with_no_dreal_rights(self):
        """has_object_permission returns False when entity has no DREAL rights"""
        # Create DREAL entity without rights
        dreal_no_rights = Entity.objects.create(name="DREAL No Rights", entity_type=Entity.EXTERNAL_ADMIN)

        request_no_rights = Mock()
        request_no_rights.entity = dreal_no_rights

        result = self.permission.has_object_permission(request_no_rights, None, self.unit_accessible)
        self.assertFalse(result)

    def test_has_object_permission_with_non_external_admin(self):
        """has_object_permission returns False for non-EXTERNAL_ADMIN entity"""
        request_producer = Mock()
        request_producer.entity = self.producer

        result = self.permission.has_object_permission(request_producer, None, self.unit_accessible)
        self.assertFalse(result)


class HasDrealRightsConfigTest(TestCase):
    """Test HasDrealRights configuration (constructor)"""

    def test_constructor_sets_allow_external(self):
        """Constructor properly sets allow_external to DREAL"""
        permission = HasDrealRights()
        self.assertEqual(permission.allow_external, [ExternalAdminRights.DREAL])

    def test_constructor_sets_allow_role_to_none(self):
        """Constructor sets allow_role to None (all roles accepted)"""
        permission = HasDrealRights()
        self.assertIsNone(permission.allow_role)

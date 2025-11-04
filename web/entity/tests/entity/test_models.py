from django.test import TestCase

from core.models import Department, Entity, EntityDepartments


class EntityGetAccessibleDepartmentsTest(TestCase):
    """Tests for Entity.get_accessible_departments() method"""

    def setUp(self):
        # Create departments
        self.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        self.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        self.dept_03 = Department.objects.create(code_dept="03", name="Allier")

        # Create entity
        self.entity = Entity.objects.create(name="Test Entity", entity_type=Entity.EXTERNAL_ADMIN)

    def test_get_accessible_departments_with_multiple_departments(self):
        """Entity with multiple departments returns all accessible departments"""
        # Associate entity with departments 01 and 02
        EntityDepartments.objects.create(entity=self.entity, department=self.dept_01)
        EntityDepartments.objects.create(entity=self.entity, department=self.dept_02)

        accessible_depts = self.entity.get_accessible_departments()

        self.assertEqual(accessible_depts.count(), 2)
        dept_codes = list(accessible_depts.values_list("code_dept", flat=True))
        self.assertIn("01", dept_codes)
        self.assertIn("02", dept_codes)
        self.assertNotIn("03", dept_codes)

    def test_get_accessible_departments_with_single_department(self):
        """Entity with single department returns only that department"""
        EntityDepartments.objects.create(entity=self.entity, department=self.dept_01)

        accessible_depts = self.entity.get_accessible_departments()

        self.assertEqual(accessible_depts.count(), 1)
        self.assertEqual(accessible_depts.first().code_dept, "01")

    def test_get_accessible_departments_with_no_departments(self):
        """Entity with no departments returns empty queryset"""
        accessible_depts = self.entity.get_accessible_departments()

        self.assertEqual(accessible_depts.count(), 0)
        self.assertFalse(accessible_depts.exists())

    def test_get_accessible_departments_returns_queryset(self):
        """get_accessible_departments() returns a Department queryset"""
        EntityDepartments.objects.create(entity=self.entity, department=self.dept_01)

        accessible_depts = self.entity.get_accessible_departments()

        # Verify it's a queryset that can be further filtered
        self.assertTrue(hasattr(accessible_depts, "filter"))
        self.assertTrue(hasattr(accessible_depts, "exclude"))
        filtered = accessible_depts.filter(code_dept="01")
        self.assertEqual(filtered.count(), 1)

    def test_get_accessible_departments_with_multiple_entities(self):
        """Department associated with multiple entities is returned correctly"""
        other_entity = Entity.objects.create(name="Other Entity", entity_type=Entity.EXTERNAL_ADMIN)

        # Both entities access department 01
        EntityDepartments.objects.create(entity=self.entity, department=self.dept_01)
        EntityDepartments.objects.create(entity=other_entity, department=self.dept_01)

        # Only entity2 accesses department 02
        EntityDepartments.objects.create(entity=other_entity, department=self.dept_02)

        # Verify each entity sees only its own departments
        entity1_depts = self.entity.get_accessible_departments()
        entity2_depts = other_entity.get_accessible_departments()

        self.assertEqual(entity1_depts.count(), 1)
        self.assertEqual(entity1_depts.first().code_dept, "01")

        self.assertEqual(entity2_depts.count(), 2)
        dept_codes = list(entity2_depts.values_list("code_dept", flat=True))
        self.assertIn("01", dept_codes)
        self.assertIn("02", dept_codes)

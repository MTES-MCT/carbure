from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from core.models import Department, Entity
from entity.models import EntityScope
from transactions.factories.depot import DepotFactory
from transactions.models import Depot


class EntityGetAccessibleDepartmentsTest(TestCase):
    """Tests for Entity.get_accessible_departments() method"""

    def setUp(self):
        # Create departments
        self.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        self.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        self.dept_03 = Department.objects.create(code_dept="03", name="Allier")

        # Create entity
        self.entity = Entity.objects.create(name="Test Entity", entity_type=Entity.EXTERNAL_ADMIN)

        # Get content type for Department
        self.dept_ct = ContentType.objects.get_for_model(Department)

    def test_get_accessible_departments_with_multiple_departments(self):
        """Entity with multiple departments returns all accessible departments"""
        # Associate entity with departments 01 and 02
        EntityScope.objects.create(entity=self.entity, content_type=self.dept_ct, object_id=self.dept_01.id)
        EntityScope.objects.create(entity=self.entity, content_type=self.dept_ct, object_id=self.dept_02.id)

        accessible_depts = self.entity.get_accessible_departments()

        self.assertEqual(accessible_depts.count(), 2)
        dept_codes = list(accessible_depts.values_list("code_dept", flat=True))
        self.assertIn("01", dept_codes)
        self.assertIn("02", dept_codes)
        self.assertNotIn("03", dept_codes)

    def test_get_accessible_departments_with_single_department(self):
        """Entity with single department returns only that department"""
        EntityScope.objects.create(entity=self.entity, content_type=self.dept_ct, object_id=self.dept_01.id)

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
        EntityScope.objects.create(entity=self.entity, content_type=self.dept_ct, object_id=self.dept_01.id)

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
        EntityScope.objects.create(entity=self.entity, content_type=self.dept_ct, object_id=self.dept_01.id)
        EntityScope.objects.create(entity=other_entity, content_type=self.dept_ct, object_id=self.dept_01.id)

        # Only entity2 accesses department 02
        EntityScope.objects.create(entity=other_entity, content_type=self.dept_ct, object_id=self.dept_02.id)

        # Verify each entity sees only its own departments
        entity1_depts = self.entity.get_accessible_departments()
        entity2_depts = other_entity.get_accessible_departments()

        self.assertEqual(entity1_depts.count(), 1)
        self.assertEqual(entity1_depts.first().code_dept, "01")

        self.assertEqual(entity2_depts.count(), 2)
        dept_codes = list(entity2_depts.values_list("code_dept", flat=True))
        self.assertIn("01", dept_codes)
        self.assertIn("02", dept_codes)


class EntityGetAccessibleDepotsTest(TestCase):
    """Tests for Entity.get_accessible_depots() method"""

    fixtures = [
        "json/countries.json",
    ]

    def setUp(self):
        # Create depots using factory
        self.depot_01 = DepotFactory.create(customs_id="FR00001", name="Dépôt 01")
        self.depot_02 = DepotFactory.create(customs_id="FR00002", name="Dépôt 02")
        self.depot_03 = DepotFactory.create(customs_id="FR00003", name="Dépôt 03")

        # Create entity
        self.entity = Entity.objects.create(name="Test Entity", entity_type=Entity.EXTERNAL_ADMIN)

        # Get content type for Depot
        self.depot_ct = ContentType.objects.get_for_model(Depot)

    def test_get_accessible_depots_with_multiple_depots(self):
        """Entity with multiple depots returns all accessible depots"""
        # Associate entity with depots 01 and 02
        EntityScope.objects.create(entity=self.entity, content_type=self.depot_ct, object_id=self.depot_01.id)
        EntityScope.objects.create(entity=self.entity, content_type=self.depot_ct, object_id=self.depot_02.id)

        accessible_depots = self.entity.get_accessible_depots()

        self.assertEqual(accessible_depots.count(), 2)
        depot_ids = list(accessible_depots.values_list("customs_id", flat=True))
        self.assertIn("FR00001", depot_ids)
        self.assertIn("FR00002", depot_ids)
        self.assertNotIn("FR00003", depot_ids)

    def test_get_accessible_depots_with_single_depot(self):
        """Entity with single depot returns only that depot"""
        EntityScope.objects.create(entity=self.entity, content_type=self.depot_ct, object_id=self.depot_01.id)

        accessible_depots = self.entity.get_accessible_depots()

        self.assertEqual(accessible_depots.count(), 1)
        self.assertEqual(accessible_depots.first().customs_id, "FR00001")

    def test_get_accessible_depots_with_no_depots(self):
        """Entity with no depots returns empty queryset"""
        accessible_depots = self.entity.get_accessible_depots()

        self.assertEqual(accessible_depots.count(), 0)
        self.assertFalse(accessible_depots.exists())

    def test_get_accessible_depots_returns_queryset(self):
        """get_accessible_depots() returns a Depot queryset"""
        EntityScope.objects.create(entity=self.entity, content_type=self.depot_ct, object_id=self.depot_01.id)

        accessible_depots = self.entity.get_accessible_depots()

        # Verify it's a queryset that can be further filtered
        self.assertTrue(hasattr(accessible_depots, "filter"))
        self.assertTrue(hasattr(accessible_depots, "exclude"))
        filtered = accessible_depots.filter(customs_id="FR00001")
        self.assertEqual(filtered.count(), 1)

    def test_get_accessible_depots_with_multiple_entities(self):
        """Depot associated with multiple entities is returned correctly"""
        other_entity = Entity.objects.create(name="Other Entity", entity_type=Entity.EXTERNAL_ADMIN)

        # Both entities access depot 01
        EntityScope.objects.create(entity=self.entity, content_type=self.depot_ct, object_id=self.depot_01.id)
        EntityScope.objects.create(entity=other_entity, content_type=self.depot_ct, object_id=self.depot_01.id)

        # Only entity2 accesses depot 02
        EntityScope.objects.create(entity=other_entity, content_type=self.depot_ct, object_id=self.depot_02.id)

        # Verify each entity sees only its own depots
        entity1_depots = self.entity.get_accessible_depots()
        entity2_depots = other_entity.get_accessible_depots()

        self.assertEqual(entity1_depots.count(), 1)
        self.assertEqual(entity1_depots.first().customs_id, "FR00001")

        self.assertEqual(entity2_depots.count(), 2)
        depot_ids = list(entity2_depots.values_list("customs_id", flat=True))
        self.assertIn("FR00001", depot_ids)
        self.assertIn("FR00002", depot_ids)

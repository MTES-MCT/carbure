from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories import BiomethaneProductionUnitFactory
from core.models import Department, Entity, ExternalAdminRights
from core.tests_utils import setup_current_user
from entity.models import EntityScope


class BiomethaneProducersViewSetTest(TestCase):
    """Tests for BiomethaneProducersViewSet"""

    @classmethod
    def setUpTestData(cls):
        # Create departments
        cls.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        cls.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        cls.dept_03 = Department.objects.create(code_dept="03", name="Allier")

        # Create DREAL entity with accessible departments 01 and 02
        cls.dreal = Entity.objects.create(name="DREAL Test", entity_type=Entity.EXTERNAL_ADMIN)
        dept_ct = ContentType.objects.get_for_model(Department)
        EntityScope.objects.create(entity=cls.dreal, content_type=dept_ct, object_id=cls.dept_01.id)
        EntityScope.objects.create(entity=cls.dreal, content_type=dept_ct, object_id=cls.dept_02.id)
        ExternalAdminRights.objects.create(entity=cls.dreal, right=ExternalAdminRights.DREAL)

        # Create another DREAL entity with different accessible department (03)
        cls.dreal_other = Entity.objects.create(name="DREAL Other", entity_type=Entity.EXTERNAL_ADMIN)
        EntityScope.objects.create(entity=cls.dreal_other, content_type=dept_ct, object_id=cls.dept_03.id)
        ExternalAdminRights.objects.create(entity=cls.dreal_other, right=ExternalAdminRights.DREAL)

        # Create producers with their production units (OneToOne relationship)
        # Producer 1 has unit in dept 01 (accessible by DREAL)
        cls.producer1 = Entity.objects.create(name="Aardvark Producer", entity_type=Entity.BIOMETHANE_PRODUCER)
        cls.unit1 = BiomethaneProductionUnitFactory.create(
            created_by=cls.producer1,
            name="Unit 1",
            department=cls.dept_01,
        )

        # Producer 2 has unit in dept 01 (accessible by DREAL)
        cls.producer2 = Entity.objects.create(name="Banana Producer", entity_type=Entity.BIOMETHANE_PRODUCER)
        cls.unit2 = BiomethaneProductionUnitFactory.create(
            created_by=cls.producer2,
            name="Unit 2",
            department=cls.dept_01,
        )

        # Producer 3 has unit in dept 02 (accessible by DREAL)
        cls.producer3 = Entity.objects.create(name="Cherry Producer", entity_type=Entity.BIOMETHANE_PRODUCER)
        cls.unit3 = BiomethaneProductionUnitFactory.create(
            created_by=cls.producer3,
            name="Unit 3",
            department=cls.dept_02,
        )

        # Producer 4 has unit in dept 03 (NOT accessible by DREAL)
        cls.producer4 = Entity.objects.create(name="Dragon Producer", entity_type=Entity.BIOMETHANE_PRODUCER)
        cls.unit4 = BiomethaneProductionUnitFactory.create(
            created_by=cls.producer4,
            name="Unit 4",
            department=cls.dept_03,
        )

        cls.producers_url = reverse("biomethane-admin-producers-list")

    def setUp(self):
        # Setup user for DREAL
        self.user = setup_current_user(
            self,
            "dreal@example.com",
            "DREAL",
            "User",
            [(self.dreal, "ADMIN")],
        )

    def test_list_producers_returns_only_accessible_producers(self):
        """list returns only producers with units in accessible departments"""
        response = self.client.get(self.producers_url, {"entity_id": self.dreal.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        producers_data = response.json()

        # Should return producer1, producer2, and producer3 (depts 01 and 02), not producer4 (dept 03)
        self.assertEqual(len(producers_data), 3)
        producer_ids = [p["id"] for p in producers_data]
        self.assertIn(self.producer1.id, producer_ids)
        self.assertIn(self.producer2.id, producer_ids)
        self.assertIn(self.producer3.id, producer_ids)
        self.assertNotIn(self.producer4.id, producer_ids)

    def test_list_producers_orders_by_name(self):
        """list returns producers ordered alphabetically by name"""
        response = self.client.get(self.producers_url, {"entity_id": self.dreal.id})

        producers_data = response.json()
        producer_names = [p["name"] for p in producers_data]

        # Should be ordered: Aardvark Producer, Banana Producer, Cherry Producer
        self.assertEqual(producer_names, ["Aardvark Producer", "Banana Producer", "Cherry Producer"])

    def test_list_producers_different_dreal_sees_different_producers(self):
        """Different DREAL entities see different producers based on their accessible departments"""
        # Setup user for other DREAL
        setup_current_user(
            self,
            "dreal_other@example.com",
            "DREAL Other",
            "User",
            [(self.dreal_other, "ADMIN")],
        )

        response = self.client.get(self.producers_url, {"entity_id": self.dreal_other.id})

        producers_data = response.json()

        # DREAL Other only has access to dept 03, so should only see producer4
        self.assertEqual(len(producers_data), 1)
        self.assertEqual(producers_data[0]["id"], self.producer4.id)

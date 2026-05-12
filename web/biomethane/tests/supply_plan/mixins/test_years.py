from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from biomethane.factories.production_unit import BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneSupplyPlan
from core.models import Department, Entity, ExternalAdminRights
from core.tests_utils import setup_current_user
from entity.models import EntityScope


class YearsSUpplyPlanAPITests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.producer_entity, "RW")],
        )

        self.years = [2024, 2025, 2015]
        BiomethaneSupplyPlan.objects.bulk_create(
            [BiomethaneSupplyPlan(producer=self.producer_entity, year=year) for year in self.years]
        )

    def test_years(self):
        response = self.client.get(reverse("biomethane-supply-plan-years"), {"entity_id": self.producer_entity.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [2015, 2024, 2025])

    def test_years_error_with_producer_using_producer_id_param(self):
        """Test that a producer cannot use producer_id param to access another producer's data (IDOR protection)."""
        producer_entity_2 = Entity.objects.create(
            name="Test Producer 2",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        params = {"entity_id": self.producer_entity.id, "producer_id": producer_entity_2.id}
        response = self.client.get(reverse("biomethane-supply-plan-years"), params)

        self.assertEqual(response.status_code, 403)

    def test_years_with_dreal_and_producer_id(self):
        """Test DREAL can access supply plan years filtered by producer_id."""
        department = Department.objects.create(code_dept="67", name="Bas-Rhin")
        BiomethaneProductionUnitFactory.create(producer=self.producer_entity, department=department)

        dreal = Entity.objects.create(name="Test DREAL", entity_type=Entity.EXTERNAL_ADMIN)
        ExternalAdminRights.objects.create(entity=dreal, right=ExternalAdminRights.DREAL)
        EntityScope.objects.create(
            entity=dreal,
            content_type=ContentType.objects.get_for_model(Department),
            object_id=department.id,
        )

        setup_current_user(self, "dreal@carbure.local", "DREAL", "gogogo", [(dreal, "ADMIN")])

        params = {"entity_id": dreal.id, "producer_id": self.producer_entity.id}
        response = self.client.get(reverse("biomethane-supply-plan-years"), params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, sorted(self.years))

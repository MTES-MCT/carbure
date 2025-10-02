from django.test import TestCase
from django.urls import reverse

from biomethane.models import BiomethaneSupplyPlan
from core.models import Entity
from core.tests_utils import setup_current_user


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

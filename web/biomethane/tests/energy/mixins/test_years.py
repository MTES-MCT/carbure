from django.test import TestCase
from django.urls import reverse

from biomethane.models import BiomethaneEnergy
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneEnergyYearsTests(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(
            name="Test Entity",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.entity, "RW")],
        )

        self.years = [2024, 2025, 2015]
        BiomethaneEnergy.objects.bulk_create([BiomethaneEnergy(producer=self.entity, year=year) for year in self.years])

    # Checks that the get_years endpoint returns the distinct years of energy objects sorted in ascending order
    def test_years(self):
        response = self.client.get(reverse("biomethane-energy-years"), {"entity_id": self.entity.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [2015, 2024, 2025])

from django.test import TestCase
from django.urls import reverse

from biomethane.models import BiomethaneDigestate
from core.models import Entity
from core.tests_utils import setup_current_user


class BiomethaneDigestateYearsTests(TestCase):
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
        BiomethaneDigestate.objects.bulk_create(
            [BiomethaneDigestate(producer=self.entity, year=year) for year in self.years]
        )

    def test_get_years(self):
        response = self.client.get(reverse("biomethane-digestate-years"), {"entity_id": self.entity.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [2015, 2024, 2025])

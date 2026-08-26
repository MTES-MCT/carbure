from datetime import date

from django.test import TestCase
from django.urls import reverse

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action


class ActionYearsTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        self.other_entity = Entity.objects.create(name="Other HRS", entity_type=Entity.HRS)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.entity, "RW")])

        ActionFactory.create(holder=self.entity, industry=Action.H2, working_date=date(2023, 1, 1))
        ActionFactory.create(holder=self.entity, industry=Action.H2, working_date=date(2025, 1, 1))
        ActionFactory.create(holder=self.entity, industry=Action.H2, working_date=date(2025, 6, 1))
        ActionFactory.create(holder=self.other_entity, industry=Action.H2, working_date=date(2024, 1, 1))
        ActionFactory.create(holder=self.entity, industry="BIOMASS", working_date=date(2022, 1, 1))

    def test_returns_sorted_years_for_the_current_entity(self):
        response = self.client.get(
            reverse("traceability-action-get-years"),
            {"entity_id": self.entity.id, "industry": Action.H2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [2023, 2025])

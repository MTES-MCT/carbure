from datetime import date

from django.test import TestCase

from core.models import Entity
from traceability.factories import ActionFactory
from traceability.filters import ActionFilter
from traceability.models import Action


class ActionFilterTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_filters_by_year(self):
        entity = Entity.objects.create(name="HRS", entity_type=Entity.HRS)
        in_2023 = ActionFactory.create(holder=entity, industry=Action.H2, working_date=date(2023, 1, 1))
        in_2025 = ActionFactory.create(holder=entity, industry=Action.H2, working_date=date(2025, 6, 1))

        filtered = ActionFilter({"year": 2025}, queryset=Action.objects.all()).qs

        self.assertIn(in_2025, filtered)
        self.assertNotIn(in_2023, filtered)

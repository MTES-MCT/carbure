from django.db import IntegrityError, transaction
from django.test import TestCase

from traceability.factories import ActionFactory


class ActionConstraintsTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_allows_null_lhv_and_density(self):
        action = ActionFactory.create(lhv=None, density=None)
        self.assertIsNone(action.lhv)
        self.assertIsNone(action.density)

    def test_rejects_zero_or_negative_factors(self):
        cases = (("lhv", 0), ("lhv", -1), ("density", 0), ("density", -1))
        for field, value in cases:
            with self.subTest(field=field, value=value), self.assertRaises(IntegrityError), transaction.atomic():
                ActionFactory.create(**{field: value})

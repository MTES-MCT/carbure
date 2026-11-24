from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from traceability.factories import ActionFactory


class ActionQuantityConstraintTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_rejects_zero_or_negative_quantity(self):
        for quantity in (Decimal("0.000"), Decimal("-1.000")):
            with self.subTest(quantity=quantity), self.assertRaises(IntegrityError), transaction.atomic():
                ActionFactory.create(quantity=quantity)

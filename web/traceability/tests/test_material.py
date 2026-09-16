from django.db import IntegrityError, transaction
from django.test import TestCase

from traceability.models import Material


class MaterialConstraintsTest(TestCase):
    def test_allows_null_lhv_and_density(self):
        material = Material.objects.create(code="MAT-NULL", name="Sans facteur")
        self.assertIsNone(material.lhv)
        self.assertIsNone(material.density)

    def test_rejects_zero_or_negative_factors(self):
        cases = (("lhv", 0), ("lhv", -1), ("density", 0), ("density", -1))
        for index, (field, value) in enumerate(cases):
            with self.subTest(field=field, value=value), self.assertRaises(IntegrityError), transaction.atomic():
                Material.objects.create(code=f"X{index}", name=f"{field} {value}", **{field: value})

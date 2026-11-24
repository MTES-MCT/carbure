from django.db import IntegrityError, transaction
from django.test import TestCase

from traceability.models import Material, MaterialTag
from traceability.models.action import Industry
from traceability.models.material_tag import Tag, values_per_type_constraint


class MaterialTagConstraintsTest(TestCase):
    def setUp(self):
        self.material = Material.objects.create(code="MAT-TAG", name="Matière avec tags", unit=Material.KG)

    def test_accepts_each_industry_value(self):
        for value in Industry.values:
            with self.subTest(value=value):
                MaterialTag.objects.create(material=self.material, type=Tag.INDUSTRY, value=value)

    def test_rejects_invalid_value_for_industry(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MaterialTag.objects.create(material=self.material, type=Tag.INDUSTRY, value="INVALID")

    def test_rejects_unconfigured_type(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MaterialTag.objects.create(material=self.material, type="other", value="FREE")

    def test_accepts_only_configured_type_value_combinations(self):
        constraint = values_per_type_constraint({"first": {"A": "A"}, "second": {"B": "B"}})
        for tag_type, value, valid in (
            ("first", "A", True),
            ("first", "B", False),
            ("second", "B", True),
            ("second", "A", False),
            ("other", "FREE", False),
            ("other", "A", False),
        ):
            with self.subTest(type=tag_type, value=value):
                result = constraint.condition.check({"type": tag_type, "value": value})
                self.assertEqual(result, valid)

    def test_full_clean_accepts_valid_combination(self):
        MaterialTag(material=self.material, type=Tag.INDUSTRY, value=Industry.H2).full_clean()

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from core.serializers import check_fields_required_when


class CheckFieldsRequiredWhenTests(SimpleTestCase):
    def test_reports_every_matching_rule(self):
        with self.assertRaises(ValidationError) as raised:
            check_fields_required_when(
                {"mode": "ROAD"},
                [
                    (lambda attrs: True, ("distance",)),
                    (lambda attrs: attrs.get("mode") == "ROAD", ("fuel",)),
                    (lambda attrs: False, ("ignored",)),
                ],
            )

        self.assertEqual(set(raised.exception.detail), {"distance", "fuel"})

    def test_accepts_present_fields(self):
        check_fields_required_when(
            {"mode": "ROAD", "fuel": "Diesel B7"},
            [(lambda attrs: attrs.get("mode") == "ROAD", ("fuel",))],
        )

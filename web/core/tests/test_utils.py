from datetime import datetime, timezone

from django.test import SimpleTestCase, override_settings

from core.utils import format_month_label, get_month_bounds_utc, truncate


class FormatMonthLabelTests(SimpleTestCase):
    def test_returns_french_month_label(self):
        self.assertEqual(format_month_label(1), "Janvier")
        self.assertEqual(format_month_label(2), "Février")

    def test_returns_original_value_when_month_invalid(self):
        self.assertEqual(format_month_label(0), 0)
        self.assertEqual(format_month_label(13), 13)
        self.assertEqual(format_month_label("foo"), "foo")


@override_settings(TIME_ZONE="Europe/Paris")
class GetMonthBoundsUtcTests(SimpleTestCase):
    def test_accounts_for_daylight_saving_start(self):
        self.assertEqual(
            get_month_bounds_utc("202503"),
            (
                datetime(2025, 2, 28, 23, tzinfo=timezone.utc),
                datetime(2025, 3, 31, 22, tzinfo=timezone.utc),
            ),
        )

    def test_accounts_for_daylight_saving_end(self):
        self.assertEqual(
            get_month_bounds_utc("202510"),
            (
                datetime(2025, 9, 30, 22, tzinfo=timezone.utc),
                datetime(2025, 10, 31, 23, tzinfo=timezone.utc),
            ),
        )


class TruncateTests(SimpleTestCase):
    def test_truncate_to_two_decimals_without_rounding(self):
        self.assertEqual(truncate(12.349, 2), 12.34)

    def test_truncate_handles_float_imprecision(self):
        self.assertEqual(truncate(12.339999999, 2), 12.34)

    def test_truncate_handles_negative_float_imprecision(self):
        self.assertEqual(truncate(-12.339999999, 2), -12.34)

    def test_truncate_handles_cached_avoided_emissions_imprecision(self):
        self.assertEqual(truncate(364.99999986719996, 2), 365.0)

    def test_truncate_negative_value_without_rounding(self):
        self.assertEqual(truncate(-214000.0, 2), -214000.0)

    def test_truncate_with_zero_decimal_places(self):
        self.assertEqual(truncate(12.99, 0), 12)

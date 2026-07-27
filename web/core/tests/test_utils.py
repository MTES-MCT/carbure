from datetime import datetime, timezone

from django.test import SimpleTestCase, override_settings

from core.utils import format_month_label, get_month_bounds_utc


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

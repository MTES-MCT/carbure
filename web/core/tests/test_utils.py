from django.test import SimpleTestCase

from core.utils import format_month_label


class FormatMonthLabelTests(SimpleTestCase):
    def test_returns_french_month_label(self):
        self.assertEqual(format_month_label(1), "Janvier")
        self.assertEqual(format_month_label(2), "Février")

    def test_returns_original_value_when_month_invalid(self):
        self.assertEqual(format_month_label(0), 0)
        self.assertEqual(format_month_label(13), 13)
        self.assertEqual(format_month_label("foo"), "foo")

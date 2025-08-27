from datetime import date
from unittest.mock import Mock, patch

from django.test import TestCase

from biomethane.decorators.check_declaration_period import get_declaration_interval


class CheckDeclarationPeriodTest(TestCase):
    def setUp(self):
        # Mock date.today() to return a fixed date
        mock_date = Mock(spec=date)
        mock_date.today.return_value = date(2025, 4, 15)
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        self.date_patcher = patch("biomethane.decorators.check_declaration_period.date", mock_date)
        self.date_patcher.start()

    def tearDown(self):
        self.date_patcher.stop()

    def test_declaration_interval_valid_for_current_year(self):
        is_valid = get_declaration_interval(2025)
        self.assertEqual(is_valid, True)

    def test_declaration_interval_invalid_for_previous_year(self):
        is_valid = get_declaration_interval(2024)
        self.assertEqual(is_valid, False)

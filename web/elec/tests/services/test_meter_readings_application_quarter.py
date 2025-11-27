from datetime import date
from unittest import TestCase

from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.meter_readings_application_quarter import (
    first_day_of_quarter,
    get_application_deadline,
    get_application_quarter,
    last_day_of_quarter,
    quarter,
)


class QuarterTest(TestCase):
    """Tests for the quarter function"""

    def test_quarter_all_months(self):
        """Test that each month returns the correct quarter"""
        # Mapping month -> expected quarter
        expected_quarters = {
            1: 1,  # January -> quarter 1
            2: 1,  # February -> quarter 1
            3: 1,  # March -> quarter 1
            4: 2,  # April -> quarter 2
            5: 2,  # May -> quarter 2
            6: 2,  # June -> quarter 2
            7: 3,  # July -> quarter 3
            8: 3,  # August -> quarter 3
            9: 3,  # September -> quarter 3
            10: 4,  # October -> quarter 4
            11: 4,  # November -> quarter 4
            12: 4,  # December -> quarter 4
        }

        for month, expected_quarter in expected_quarters.items():
            test_date = date(2024, month, 15)
            year, quarter_num = quarter(test_date)
            self.assertEqual(year, 2024, f"Year should be 2024 for month {month}")
            self.assertEqual(quarter_num, expected_quarter, f"Month {month} should return quarter {expected_quarter}")


class FirstDayOfQuarterTest(TestCase):
    """Tests for the first_day_of_quarter function"""

    def test_first_day_all_quarters(self):
        """Test that each quarter returns the correct first day"""
        # Mapping quarter -> expected (month, day)
        expected_dates = {
            1: (1, 1),  # quarter 1 -> January 1st
            2: (4, 1),  # quarter 2 -> April 1st
            3: (7, 1),  # quarter 3 -> July 1st
            4: (10, 1),  # quarter 4 -> October 1st
        }

        for quarter_num, (expected_month, expected_day) in expected_dates.items():
            result = first_day_of_quarter(2024, quarter_num)
            self.assertEqual(
                result,
                date(2024, expected_month, expected_day),
                f"Quarter {quarter_num} should start on {expected_day}/{expected_month}/2024",
            )

    def test_first_day_different_years(self):
        """Test with different years"""
        test_cases = [
            (2023, 1, date(2023, 1, 1)),
            (2023, 2, date(2023, 4, 1)),
        ]

        for year, quarter_num, expected_date in test_cases:
            result = first_day_of_quarter(year, quarter_num)
            self.assertEqual(result, expected_date, f"Quarter {quarter_num} of year {year} should start on {expected_date}")


class LastDayOfQuarterTest(TestCase):
    """Tests for the last_day_of_quarter function"""

    def test_last_day_all_quarters(self):
        """Test that each quarter returns the correct last day"""
        # Mapping quarter -> expected (month, day)
        expected_dates = {
            1: (3, 31),  # quarter 1 -> March 31st
            2: (6, 30),  # quarter 2 -> June 30th
            3: (9, 30),  # quarter 3 -> September 30th
            4: (12, 31),  # quarter 4 -> December 31st
        }

        for quarter_num, (expected_month, expected_day) in expected_dates.items():
            result = last_day_of_quarter(2024, quarter_num)
            self.assertEqual(
                result,
                date(2024, expected_month, expected_day),
                f"Quarter {quarter_num} should end on {expected_day}/{expected_month}/2024",
            )


class GetApplicationQuarterTest(TestCase):
    """Tests for the get_application_quarter function"""

    def test_application_quarter_in_last_10_days(self):
        """Test that dates in the last 10 days return the current quarter"""
        # Test for each quarter: last day, 5 days before, 10 days before
        test_cases = [
            # Quarter 1 (March 31st)
            (date(2024, 3, 31), 2024, 1),  # last day
            (date(2024, 3, 26), 2024, 1),  # 5 days before
            (date(2024, 3, 21), 2024, 1),  # 10 days before
            # Quarter 2 (June 30th)
            (date(2024, 6, 30), 2024, 2),  # last day
            (date(2024, 6, 25), 2024, 2),  # 5 days before
            (date(2024, 6, 20), 2024, 2),  # 10 days before
            # Quarter 3 (September 30th)
            (date(2024, 9, 30), 2024, 3),  # last day
            (date(2024, 9, 25), 2024, 3),  # 5 days before
            (date(2024, 9, 20), 2024, 3),  # 10 days before
            # Quarter 4 (December 31st)
            (date(2024, 12, 31), 2024, 4),  # last day
            (date(2024, 12, 26), 2024, 4),  # 5 days before
            (date(2024, 12, 21), 2024, 4),  # 10 days before
        ]

        for test_date, expected_year, expected_quarter in test_cases:
            year, quarter_num = get_application_quarter(test_date)
            self.assertEqual(
                (year, quarter_num),
                (expected_year, expected_quarter),
                f"Date {test_date} should return quarter {expected_quarter} of {expected_year}",
            )

    def test_application_quarter_early_in_quarter(self):
        """Test that dates at the beginning/middle of quarter return the previous quarter"""
        test_cases = [
            # Beginning of quarter 1 -> quarter 4 of previous year
            (date(2024, 1, 1), 2023, 4),  # January 1st
            (date(2024, 1, 15), 2023, 4),  # mid January
            (date(2024, 2, 10), 2023, 4),  # early February
            (date(2024, 3, 10), 2023, 4),  # early March (11 days before end)
            # Beginning of quarter 2 -> quarter 1
            (date(2024, 4, 1), 2024, 1),  # April 1st
            (date(2024, 4, 15), 2024, 1),  # mid April
            (date(2024, 5, 10), 2024, 1),  # early May
            (date(2024, 6, 10), 2024, 1),  # early June (20 days before end)
            # Beginning of quarter 3 -> quarter 2
            (date(2024, 7, 1), 2024, 2),  # July 1st
            (date(2024, 7, 15), 2024, 2),  # mid July
            (date(2024, 8, 10), 2024, 2),  # early August
            (date(2024, 9, 10), 2024, 2),  # early September (20 days before end)
            # Beginning of quarter 4 -> quarter 3
            (date(2024, 10, 1), 2024, 3),  # October 1st
            (date(2024, 10, 17), 2024, 3),  # mid October
            (date(2024, 11, 10), 2024, 3),  # early November
            (date(2024, 12, 10), 2024, 3),  # early December (21 days before end)
        ]

        for test_date, expected_year, expected_quarter in test_cases:
            year, quarter_num = get_application_quarter(test_date)
            self.assertEqual(
                (year, quarter_num),
                (expected_year, expected_quarter),
                f"Date {test_date} should return quarter {expected_quarter} of {expected_year}",
            )


class GetApplicationDeadlineTest(TestCase):
    """Tests for the get_application_deadline function"""

    def test_deadline_calculation_all_quarters(self):
        """Test that the deadline is correctly calculated (last day of quarter + 15 days)"""
        # Mapping quarter -> (last day, expected deadline)
        expected_deadlines = {
            1: (date(2024, 3, 31), date(2024, 4, 15)),  # quarter 1 -> April 15th
            2: (date(2024, 6, 30), date(2024, 7, 15)),  # quarter 2 -> July 15th
            3: (date(2024, 9, 30), date(2024, 10, 15)),  # quarter 3 -> October 15th
            4: (date(2024, 12, 31), date(2025, 1, 15)),  # quarter 4 -> January 15th next year
        }

        for quarter_num, (last_day, expected_deadline) in expected_deadlines.items():
            # Use a date before the deadline for the test
            current_date = last_day
            deadline, _ = get_application_deadline(current_date, 2024, quarter_num)
            self.assertEqual(
                deadline,
                expected_deadline,
                f"Quarter {quarter_num} should have a deadline on {expected_deadline}",
            )

    def test_status_critical(self):
        """Test that CRITICAL status is returned when the deadline is passed"""
        test_cases = [
            # Quarter 1 (deadline: April 15th 2024)
            (date(2024, 4, 16), 2024, 1, ElecMeterReadingApplication.CRITICAL),  # 1 day after
            (date(2024, 4, 20), 2024, 1, ElecMeterReadingApplication.CRITICAL),  # 5 days after
            (date(2024, 5, 1), 2024, 1, ElecMeterReadingApplication.CRITICAL),  # 16 days after
            # Quarter 2 (deadline: July 15th 2024)
            (date(2024, 7, 16), 2024, 2, ElecMeterReadingApplication.CRITICAL),  # 1 day after
            (date(2024, 8, 1), 2024, 2, ElecMeterReadingApplication.CRITICAL),  # 17 days after
        ]

        for current_date, year, quarter_num, expected_status in test_cases:
            _, status = get_application_deadline(current_date, year, quarter_num)
            self.assertEqual(
                status,
                expected_status,
                f"Date {current_date} should return CRITICAL status for quarter {quarter_num} of {year}",
            )

    def test_status_high(self):
        """Test that HIGH status is returned when there are 10 days or less remaining"""
        test_cases = [
            # Quarter 1 (deadline: April 15th 2024)
            (date(2024, 4, 15), 2024, 1, ElecMeterReadingApplication.HIGH),  # deadline day
            (date(2024, 4, 10), 2024, 1, ElecMeterReadingApplication.HIGH),  # 5 days before
            (date(2024, 4, 5), 2024, 1, ElecMeterReadingApplication.HIGH),  # 10 days before
            # Quarter 2 (deadline: July 15th 2024)
            (date(2024, 7, 15), 2024, 2, ElecMeterReadingApplication.HIGH),  # deadline day
            (date(2024, 7, 10), 2024, 2, ElecMeterReadingApplication.HIGH),  # 5 days before
            (date(2024, 7, 5), 2024, 2, ElecMeterReadingApplication.HIGH),  # 10 days before
            # Quarter 3 (deadline: October 15th 2024)
            (date(2024, 10, 15), 2024, 3, ElecMeterReadingApplication.HIGH),  # deadline day
            (date(2024, 10, 6), 2024, 3, ElecMeterReadingApplication.HIGH),  # 9 days before
            # Quarter 4 (deadline: January 15th 2025)
            (date(2025, 1, 15), 2024, 4, ElecMeterReadingApplication.HIGH),  # deadline day
            (date(2025, 1, 5), 2024, 4, ElecMeterReadingApplication.HIGH),  # 10 days before
        ]

        for current_date, year, quarter_num, expected_status in test_cases:
            _, status = get_application_deadline(current_date, year, quarter_num)
            self.assertEqual(
                status,
                expected_status,
                f"Date {current_date} should return HIGH status for quarter {quarter_num} of {year}",
            )

    def test_status_low(self):
        """Test that LOW status is returned when there are more than 10 days remaining"""
        test_cases = [
            # Quarter 1 (deadline: April 15th 2024)
            (date(2024, 4, 4), 2024, 1, ElecMeterReadingApplication.LOW),  # 11 days before
            (date(2024, 3, 31), 2024, 1, ElecMeterReadingApplication.LOW),  # 15 days before
            (date(2024, 3, 20), 2024, 1, ElecMeterReadingApplication.LOW),  # 26 days before
            # Quarter 2 (deadline: July 15th 2024)
            (date(2024, 7, 4), 2024, 2, ElecMeterReadingApplication.LOW),  # 11 days before
            (date(2024, 6, 30), 2024, 2, ElecMeterReadingApplication.LOW),  # 15 days before
            (date(2024, 6, 1), 2024, 2, ElecMeterReadingApplication.LOW),  # 44 days before
            # Quarter 3 (deadline: October 15th 2024)
            (date(2024, 10, 4), 2024, 3, ElecMeterReadingApplication.LOW),  # 11 days before
            (date(2024, 9, 30), 2024, 3, ElecMeterReadingApplication.LOW),  # 15 days before
            (date(2024, 9, 1), 2024, 3, ElecMeterReadingApplication.LOW),  # 44 days before
            # Quarter 4 (deadline: January 15th 2025)
            (date(2025, 1, 4), 2024, 4, ElecMeterReadingApplication.LOW),  # 11 days before
            (date(2024, 12, 31), 2024, 4, ElecMeterReadingApplication.LOW),  # 15 days before
            (date(2024, 12, 1), 2024, 4, ElecMeterReadingApplication.LOW),  # 45 days before
        ]

        for current_date, year, quarter_num, expected_status in test_cases:
            _, status = get_application_deadline(current_date, year, quarter_num)
            self.assertEqual(
                status,
                expected_status,
                f"Date {current_date} should return LOW status for quarter {quarter_num} of {year}",
            )

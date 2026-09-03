from django.test import TestCase
from rest_framework import serializers

from biomethane.serializers.fields import DepartmentField, EuropeanFloatField


class EuropeanFloatFieldTests(TestCase):
    """Test cases for EuropeanFloatField"""

    def setUp(self):
        """Set up test data"""
        self.field = EuropeanFloatField()

    def test_accepts_american_decimal_notation(self):
        """Test that field accepts American decimal notation (dot)"""
        result = self.field.to_internal_value("123.45")
        self.assertEqual(result, 123.45)

    def test_accepts_european_decimal_notation(self):
        """Test that field accepts European decimal notation (comma)"""
        result = self.field.to_internal_value("123,45")
        self.assertEqual(result, 123.45)

    def test_accepts_integer_values(self):
        """Test that field accepts integer values"""
        result = self.field.to_internal_value("123")
        self.assertEqual(result, 123.0)

    def test_accepts_float_values(self):
        """Test that field accepts float values directly"""
        result = self.field.to_internal_value(123.45)
        self.assertEqual(result, 123.45)

    def test_handles_negative_values(self):
        """Test that field handles negative values correctly"""
        result = self.field.to_internal_value("-123,45")
        self.assertEqual(result, -123.45)

    def test_rejects_invalid_float_strings(self):
        """Test that field rejects invalid float strings"""
        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("not_a_number")

        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("12.34.56")

        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("12,34,56")


class DepartmentFieldTests(TestCase):
    """Test cases for DepartmentField"""

    def setUp(self):
        """Set up test data"""
        self.field = DepartmentField()

    def test_extracts_department_code_from_formatted_string(self):
        """Test that field extracts department code from 'code - name' format"""
        result = self.field.to_internal_value("75 - Paris")
        self.assertEqual(result, "75")

        result = self.field.to_internal_value("2A - Corse-du-Sud")
        self.assertEqual(result, "2A")

    def test_handles_department_code_only(self):
        """Test that field handles department code without name"""
        result = self.field.to_internal_value("75")
        self.assertEqual(result, "75")

    def test_handles_overseas_departments(self):
        """Test that field handles overseas departments correctly"""
        result = self.field.to_internal_value("971 - Guadeloupe")
        self.assertEqual(result, "971")

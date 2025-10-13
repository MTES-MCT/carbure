from django.test import TestCase
from rest_framework import serializers

from biomethane.serializers.fields import DepartmentField, EuropeanFloatField, LabelChoiceField


class LabelChoiceFieldTests(TestCase):
    """Test cases for LabelChoiceField"""

    def setUp(self):
        """Set up test data"""
        self.choices = [
            ("choice1", "Choice 1"),
            ("choice2", "Choice 2"),
            ("choice3", "Choice 3"),
        ]
        self.field = LabelChoiceField(choices=self.choices)

    def test_accepts_valid_choice_value(self):
        """Test that field accepts valid choice values"""
        result = self.field.to_internal_value("choice1")
        self.assertEqual(result, "choice1")

    def test_accepts_valid_choice_label(self):
        """Test that field accepts valid choice labels"""
        result = self.field.to_internal_value("Choice 1")
        self.assertEqual(result, "choice1")

    def test_accepts_choice_label_case_insensitive(self):
        """Test that field accepts choice labels in different cases"""
        result = self.field.to_internal_value("CHOICE 1")
        self.assertEqual(result, "choice1")

        result = self.field.to_internal_value("cHoiCe 2")
        self.assertEqual(result, "choice2")

    def test_rejects_invalid_choice(self):
        """Test that field rejects invalid choices"""
        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("invalid_choice")

        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("Unknown Label")

    def test_empty_choices(self):
        """Test field behavior with empty choices"""
        empty_field = LabelChoiceField(choices=[])

        with self.assertRaises(serializers.ValidationError):
            empty_field.to_internal_value("any_value")

    def test_non_string_input(self):
        """Test field behavior with non-string input"""
        numeric_choices = [(1, "One"), (2, "Two")]
        numeric_field = LabelChoiceField(choices=numeric_choices)

        result = numeric_field.to_internal_value(1)
        self.assertEqual(result, 1)

        result = numeric_field.to_internal_value("One")
        self.assertEqual(result, 1)


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

from django.test import TestCase
from rest_framework import serializers

from core.serializer_fields import LabelChoiceField


class LabelChoiceFieldTests(TestCase):
    def setUp(self):
        self.choices = [
            ("choice1", "Choice 1"),
            ("choice2", "Choice 2"),
            ("choice3", "Choice 3"),
        ]
        self.field = LabelChoiceField(choices=self.choices)

    def test_accepts_valid_choice_value(self):
        result = self.field.to_internal_value("choice1")
        self.assertEqual(result, "choice1")

    def test_accepts_valid_choice_label(self):
        result = self.field.to_internal_value("Choice 1")
        self.assertEqual(result, "choice1")

    def test_accepts_choice_label_case_insensitive(self):
        result = self.field.to_internal_value("CHOICE 1")
        self.assertEqual(result, "choice1")

        result = self.field.to_internal_value("cHoiCe 2")
        self.assertEqual(result, "choice2")

    def test_rejects_invalid_choice(self):
        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("invalid_choice")

        with self.assertRaises(serializers.ValidationError):
            self.field.to_internal_value("Unknown Label")

    def test_empty_choices(self):
        empty_field = LabelChoiceField(choices=[])

        with self.assertRaises(serializers.ValidationError):
            empty_field.to_internal_value("any_value")

    def test_non_string_input(self):
        numeric_choices = [(1, "One"), (2, "Two")]
        numeric_field = LabelChoiceField(choices=numeric_choices)

        result = numeric_field.to_internal_value(1)
        self.assertEqual(result, 1)

        result = numeric_field.to_internal_value("One")
        self.assertEqual(result, 1)

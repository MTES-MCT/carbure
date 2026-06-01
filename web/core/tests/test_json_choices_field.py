from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps

from core.models.fields import JSONChoiceField


class JSONChoiceFieldTests(SimpleTestCase):
    CHOICES = [
        ("A", "Alpha"),
        ("B", "Beta"),
    ]

    def test_accepts_valid_list_values(self):
        field = JSONChoiceField(choices=self.CHOICES)
        field.validate(["A", "B"], model_instance=None)

    def test_rejects_non_list_values(self):
        field = JSONChoiceField(choices=self.CHOICES)

        with self.assertRaises(ValidationError):
            field.validate("A", model_instance=None)

    def test_rejects_invalid_values(self):
        field = JSONChoiceField(choices=self.CHOICES)

        with self.assertRaises(ValidationError):
            field.validate(["A", "Z"], model_instance=None)

    def test_get_labels_returns_display_values(self):
        field = JSONChoiceField(choices=self.CHOICES)
        self.assertEqual(field.get_labels(["A", "B"]), ["Alpha", "Beta"])

    def test_formfield_uses_json_widget_not_select(self):
        field = JSONChoiceField(choices=self.CHOICES)
        form_field = field.formfield()

        self.assertIsInstance(form_field, forms.JSONField)
        self.assertNotIsInstance(form_field, forms.TypedChoiceField)

    @isolate_apps("core")
    def test_get_field_display_is_overridden_for_json_list(self):
        class DummyModel(models.Model):
            labels = JSONChoiceField(choices=self.CHOICES, default=list)

            class Meta:
                app_label = "core"

        instance = DummyModel()
        instance.labels = ["A", "B"]

        self.assertEqual(instance.get_labels_display(), "Alpha, Beta")

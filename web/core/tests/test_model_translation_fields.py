from unittest import TestCase

from core.services import model_translation_fields


class ModelTranslationFieldsTests(TestCase):
    def test_uses_model_translation_key_when_defined(self):
        fields = model_translation_fields.get_verbose_fields_by_model_for_module("biomethane")

        self.assertIn("contract", fields)
        self.assertIn("digestate", fields)
        self.assertIn("energy", fields)
        self.assertIn("injection", fields)
        self.assertIn("production", fields)
        self.assertIn("supply_plan", fields)

    def test_replaces_spaces_without_stripping_model_key(self):
        class DummyModel:
            translation_model_key = "  custom key  "

        model_key = model_translation_fields._get_translation_model_key(DummyModel)
        self.assertEqual(model_key, "__custom_key__")

    def test_excludes_technical_fields_from_translation_keys(self):
        fields = model_translation_fields.get_verbose_fields_for_translation(["biomethane"])
        self.assertFalse(any(key.endswith(".id") for key in fields))

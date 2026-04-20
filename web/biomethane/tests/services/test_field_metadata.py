from unittest import TestCase

from biomethane.services.field_metadata import get_verbose_fields_by_model


class FieldMetadataServiceTests(TestCase):
    def test_returns_expected_model_keys(self):
        result = get_verbose_fields_by_model()

        self.assertEqual(
            list(result.keys()),
            ["digestate", "energy", "supply_plan", "contract", "production", "injection"],
        )

    def test_only_returns_fields_with_verbose_name(self):
        result = get_verbose_fields_by_model()

        for model_key, fields in result.items():
            self.assertGreater(len(fields), 0, f"{model_key} should expose at least one field")

            for field_name, verbose_name in fields.items():
                self.assertTrue(field_name)
                self.assertTrue(verbose_name)

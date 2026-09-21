from django.test import SimpleTestCase
from django.utils.translation import gettext as _
from rest_framework import serializers

from core.excel_importer import ExcelImporter, ExcelValidationError
from core.serializer_validators import UniqueInListSerializer


class _ListSerializer(UniqueInListSerializer):
    unique_fields = ["code"]


class _ItemSerializer(serializers.Serializer):
    code = serializers.CharField()
    label = serializers.CharField()

    class Meta:
        list_serializer_class = _ListSerializer


class UniqueInListSerializerTests(SimpleTestCase):
    def test_accepts_unique_values(self):
        serializer = _ItemSerializer(
            data=[{"code": "A", "label": "one"}, {"code": "B", "label": "two"}],
            many=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_duplicates_on_every_occurrence(self):
        serializer = _ItemSerializer(
            data=[{"code": "A", "label": "one"}, {"code": "B", "label": "two"}, {"code": "A", "label": "three"}],
            many=True,
        )
        self.assertFalse(serializer.is_valid())
        message = _("Cette valeur est déjà utilisée ailleurs dans le fichier.")
        self.assertEqual(serializer.errors[0], {"code": [message]})
        self.assertEqual(serializer.errors[1], {})
        self.assertEqual(serializer.errors[2], {"code": [message]})

    def test_ignores_empty_values(self):
        class BlankCodeSerializer(serializers.Serializer):
            code = serializers.CharField(allow_blank=True)
            label = serializers.CharField()

            class Meta:
                list_serializer_class = _ListSerializer

        serializer = BlankCodeSerializer(
            data=[{"code": "A", "label": "one"}, {"code": "", "label": "two"}, {"code": "", "label": "three"}],
            many=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_does_not_check_fields_outside_unique_fields(self):
        serializer = _ItemSerializer(
            data=[{"code": "A", "label": "same"}, {"code": "B", "label": "same"}],
            many=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_excel_importer_keeps_errors_on_the_field(self):
        serializer = _ItemSerializer(
            data=[{"code": "A", "label": "one"}, {"code": "A", "label": "two"}],
            many=True,
        )
        with self.assertRaises(ExcelValidationError) as context:
            ExcelImporter.validate_retrieved_data(serializer, config={"header_row": 0}, nb_rows=2)

        self.assertEqual(context.exception.validation_errors[0]["row"], 2)
        self.assertIn("code", context.exception.validation_errors[0]["errors"])
        self.assertEqual(context.exception.validation_errors[1]["row"], 3)
        self.assertIn("code", context.exception.validation_errors[1]["errors"])

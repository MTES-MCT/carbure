from unittest import TestCase

from edelivery.ebms.converters import QuantityConverter, UDBConversionError


class QuantityConverterTest(TestCase):
    def test_converts_udb_quantity_to_carbure_lot_attribute_value(self):
        conversion_mapping = {"UDB_UNIT": ("some_model_attribute", (lambda x: x * 2))}
        converter = QuantityConverter(conversion_mapping)
        self.assertEqual({"some_model_attribute": 20}, converter.from_udb("UDB_UNIT", 10))

    def test_raises_udb_conversion_error_if_unit_unknown(self):
        conversion_mapping = {"UDB_UNIT": ("some_model_attribute", (lambda x: x * 2))}
        converter = QuantityConverter(conversion_mapping)
        with self.assertRaises(UDBConversionError) as context:
            converter.from_udb("UNKNOWN_UNIT", 10)

        self.assertEqual("Unknown UDB Unit: UNKNOWN_UNIT", context.exception.message)

from unittest import TestCase

from edelivery.ebms.converters import QuantityConverter


class QuantityConverterTest(TestCase):
    def test_converts_udb_quantity_to_carbure_lot_attribute_value(self):
        conversion_mapping = {"UDB_UNIT": ("some_model_attribute", (lambda x: x * 2))}
        converter = QuantityConverter(conversion_mapping)
        self.assertEqual({"some_model_attribute": 20}, converter.from_udb("UDB_UNIT", 10))

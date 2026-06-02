from unittest import TestCase

from edelivery.ebms.converters import (
    CertificateStatusConverter,
    MaterialConverter,
    QuantityConverter,
    TransactionStatusConverter,
    UDBConversionError,
)


class CertificateStatusConverterTest(TestCase):
    def test_converts_carbure_certificate_status_to_udb_status(self):
        conversion_mapping = {"UDB_STATUS": "CARBURE_STATUS"}
        converter = CertificateStatusConverter(conversion_mapping)
        self.assertEqual("UDB_STATUS", converter.to_udb("CARBURE_STATUS"))

    def test_raises_carbure_conversion_error_if_status_unknown(self):
        conversion_mapping = {}
        converter = CertificateStatusConverter(conversion_mapping)
        with self.assertRaises(UDBConversionError) as context:
            converter.to_udb("UNKNOWN_STATUS")

        self.assertEqual("Unknown Carbure Status: UNKNOWN_STATUS", context.exception.message)


class MaterialConverterTest(TestCase):
    def test_converts_udb_fame_to_carbure_biofuel(self):
        converter = MaterialConverter({"FBM0003": "EMAG"})
        carbure_biofuel_code = converter.from_udb_biofuel_code("FBM0003")
        self.assertEqual("EMAG", carbure_biofuel_code)

    def test_converts_udb_rapeseed_to_carbure_feedstock(self):
        converter = MaterialConverter({"URWR001": "COLZA"})
        carbure_feedstock_code = converter.from_udb_feedstock_code("URWR001")
        self.assertEqual("COLZA", carbure_feedstock_code)

    def test_raises_error_if_udb_code_unknown(self):
        converter = MaterialConverter({})
        with self.assertRaises(UDBConversionError) as context:
            converter.from_udb_feedstock_code("unknown_code")

        self.assertEqual("Unknown UDB Material code: unknown_code", context.exception.message)


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


class TransactionStatusConverterTest(TestCase):
    def test_converts_udb_transaction_status_to_carbure_lot_status(self):
        conversion_mapping = {"UDB_STATUS": "CARBURE_STATUS"}
        converter = TransactionStatusConverter(conversion_mapping)
        self.assertEqual("CARBURE_STATUS", converter.from_udb("UDB_STATUS"))

    def test_raises_udb_conversion_error_if_status_unknown(self):
        conversion_mapping = {}
        converter = TransactionStatusConverter(conversion_mapping)
        with self.assertRaises(UDBConversionError) as context:
            converter.from_udb("UNKNOWN_STATUS")

        self.assertEqual("Unknown UDB Status: UNKNOWN_STATUS", context.exception.message)

from datetime import date
from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.transaction import Transaction
from edelivery.tests.ebms.fixtures.udb_xml_data import transaction_data


class TransactionTest(TestCase):
    def setUp(self):
        self.patched_from_national_trade_register = patch(
            "edelivery.ebms.transaction.from_national_trade_register",
        ).start()
        self.patched_from_national_trade_register.return_value = 99999

    def tearDown(self):
        patch.stopall()

    def test_knows_its_udb_transaction_id(self):
        xml_data = transaction_data(udb_transaction_id="TRN-0000000000001-1234567890")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("TRN-0000000000001-1234567890", transaction.udb_transaction_id())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual("TRN-0000000000001-1234567890", lot_attributes["udb_transaction_id"])

    def test_knows_its_loading_date_in_ISO_format(self):
        xml_data = transaction_data(loading_date="2026-02-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual(date(2026, 2, 22), transaction.loading_date())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual(date(2026, 2, 22), lot_attributes["dispatch_date"])

    def test_knows_its_delivery_date_in_ISO_format(self):
        xml_data = transaction_data(delivery_date="2025-12-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual(date(2025, 12, 22), transaction.delivery_date())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual(date(2025, 12, 22), lot_attributes["delivery_date"])

    def test_knows_its_supplier(self):
        self.patched_from_national_trade_register.return_value = 12345

        xml_data = transaction_data(supplier_id="FR_SIREN_CD123456789")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("FR_SIREN_CD123456789", transaction.supplier_id())
        self.patched_from_national_trade_register.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        self.patched_from_national_trade_register.assert_any_call("FR_SIREN_CD123456789")
        self.assertEqual(12345, lot_attributes["carbure_supplier_id"])

    def test_knows_its_client(self):
        self.patched_from_national_trade_register.return_value = 12345

        xml_data = transaction_data(client_id="FR_SIREN_CD123123123")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("FR_SIREN_CD123123123", transaction.client_id())
        self.patched_from_national_trade_register.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        self.patched_from_national_trade_register.assert_any_call("FR_SIREN_CD123123123")
        self.assertEqual(12345, lot_attributes["carbure_client_id"])

    def test_translates_its_status(self):
        xml_data = transaction_data(status="CREATED")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("CREATED", transaction.status())
        self.assertEqual("DRAFT", transaction.carbure_status())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual("DRAFT", lot_attributes["lot_status"])

    @patch("edelivery.ebms.transaction.MaterialConverter")
    def test_knows_its_feedstock_code(self, patched_MaterialConverter):
        patched_from_udb_feedstock_code = patched_MaterialConverter.return_value.from_udb_feedstock_code
        patched_from_udb_feedstock_code.return_value = "BETTERAVE"

        xml_data = transaction_data(feedstock={"code": "URWS023", "name": "Sugar beet"})
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("URWS023", transaction.feedstock_code())
        patched_from_udb_feedstock_code.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        patched_from_udb_feedstock_code.assert_called_with("URWS023")
        self.assertEqual("BETTERAVE", lot_attributes["feedstock_code"])

    @patch("edelivery.ebms.transaction.MaterialConverter")
    def test_knows_its_biofuel_code(self, patched_MaterialConverter):
        patched_from_udb_biofuel_code = patched_MaterialConverter.return_value.from_udb_biofuel_code
        patched_from_udb_biofuel_code.return_value = "BIOGAZ"

        xml_data = transaction_data(biofuel={"code": "SFC0015", "name": "Biogas"})
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("SFC0015", transaction.biofuel_code())
        patched_from_udb_biofuel_code.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        patched_from_udb_biofuel_code.assert_called_with("SFC0015")
        self.assertEqual("BIOGAZ", lot_attributes["biofuel_code"])

    def test_knows_its_biofuel_quantity_and_unit(self):
        xml_data = transaction_data(quantity={"unit": "MWh", "value": 10})
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("MWh", transaction.unit())
        self.assertEqual(10, transaction.quantity())

    @patch("edelivery.ebms.transaction.QuantityConverter")
    def test_converts_quantity_data(self, patched_QuantityConverter):
        patched_QuantityConverter.return_value.from_udb.return_value = {"lhv_amount": 3600 * 10}

        xml_data = transaction_data(quantity={"unit": "MWh", "value": 10})
        transaction = Transaction.from_xml(xml_data)

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual(3600 * 10, lot_attributes["lhv_amount"])

        # should not be computed at this stage
        self.assertNotIn("quantity", lot_attributes)
        self.assertNotIn("volume", lot_attributes)
        self.assertNotIn("weight", lot_attributes)

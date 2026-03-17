from unittest import TestCase
from unittest.mock import patch

from core.models import Biocarburant, Entity, MatierePremiere
from edelivery.ebms.transaction import Transaction
from edelivery.tests.ebms.fixtures.udb_xml_data import transaction_data


class TransactionTest(TestCase):
    def setUp(self):
        self.patched_MaterialConverter = patch("edelivery.ebms.transaction.MaterialConverter").start()
        self.patched_MaterialConverter.return_value.from_udb_feedstock_code.return_value = MatierePremiere()
        self.patched_MaterialConverter.return_value.from_udb_biofuel_code.return_value = Biocarburant()

        self.patched_from_national_trade_register = patch(
            "edelivery.ebms.transaction.from_national_trade_register",
        ).start()
        self.patched_from_national_trade_register.return_value = Entity()

        self.patched_compute_lot_quantity = patch("edelivery.ebms.transaction.compute_lot_quantity").start()
        self.patched_compute_lot_quantity.return_value = {}

    def tearDown(self):
        patch.stopall()

    def test_knows_its_udb_transaction_id(self):
        xml_data = transaction_data(udb_transaction_id="TRN-0000000000001-1234567890")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("TRN-0000000000001-1234567890", transaction.udb_transaction_id())

    def test_knows_its_loading_date_in_ISO_format(self):
        xml_data = transaction_data(loading_date="2026-02-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("2026-02-22", transaction.iso_format_loading_date())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual("2026-02-22", lot_attributes["dispatch_date"])

    def test_knows_its_delivery_date_in_ISO_format(self):
        xml_data = transaction_data(delivery_date="2025-12-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("2025-12-22", transaction.iso_format_delivery_date())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual("2025-12-22", lot_attributes["delivery_date"])

    def test_knows_its_delivery_month_period(self):
        xml_data = transaction_data(delivery_date="2025-12-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual(202512, transaction.period())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual(202512, lot_attributes["period"])

    def test_uses_dispatch_month_period_when_delivery_date_not_set(self):
        xml_data = transaction_data(delivery_date=None, loading_date="2026-02-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        lot_attributes = transaction.to_lot_attributes()
        self.assertTrue("delivery_date" not in lot_attributes)
        self.assertEqual(202602, lot_attributes["period"])

    def test_knows_its_year(self):
        xml_data = transaction_data(delivery_date="2025-12-22T00:00:00.000Z")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual(2025, transaction.year())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual(2025, lot_attributes["year"])

    def test_knows_its_supplier(self):
        entity = Entity(name="Some Entity")
        self.patched_from_national_trade_register.return_value = entity

        xml_data = transaction_data(supplier_id="FR_SIREN_CD123456789")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("FR_SIREN_CD123456789", transaction.supplier_id())
        self.patched_from_national_trade_register.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        self.patched_from_national_trade_register.assert_any_call("FR_SIREN_CD123456789")
        self.assertEqual("Some Entity", lot_attributes["carbure_supplier"].name)

    def test_knows_its_client(self):
        entity = Entity(name="Some Entity")
        self.patched_from_national_trade_register.return_value = entity

        xml_data = transaction_data(client_id="FR_SIREN_CD123123123")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("FR_SIREN_CD123123123", transaction.client_id())
        self.patched_from_national_trade_register.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        self.patched_from_national_trade_register.assert_any_call("FR_SIREN_CD123123123")
        self.assertEqual("Some Entity", lot_attributes["carbure_client"].name)

    def test_translates_its_status(self):
        xml_data = transaction_data(status="CREATED")
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("CREATED", transaction.status())

        lot_attributes = transaction.to_lot_attributes()
        self.assertEqual("DRAFT", lot_attributes["lot_status"])

    def test_knows_its_feedstock_code(self):
        patched_from_udb_feedstock_code = self.patched_MaterialConverter.return_value.from_udb_feedstock_code
        patched_from_udb_feedstock_code.return_value = MatierePremiere(name="Betterave")

        xml_data = transaction_data(feedstock={"code": "URWS023", "name": "Sugar beet"})
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("URWS023", transaction.feedstock_code())
        patched_from_udb_feedstock_code.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        patched_from_udb_feedstock_code.assert_called_with("URWS023")
        self.assertEqual("Betterave", lot_attributes["feedstock"].name)

    def test_knows_its_biofuel_code(self):
        patched_from_udb_biofuel_code = self.patched_MaterialConverter.return_value.from_udb_biofuel_code
        patched_from_udb_biofuel_code.return_value = Biocarburant(name="Biogaz")

        xml_data = transaction_data(biofuel={"code": "SFC0015", "name": "Biogas"})
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("SFC0015", transaction.biofuel_code())
        patched_from_udb_biofuel_code.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        patched_from_udb_biofuel_code.assert_called_with("SFC0015")
        self.assertEqual("Biogaz", lot_attributes["biofuel"].name)

    def test_knows_its_biofuel_quantity_and_unit(self):
        xml_data = transaction_data(quantity={"unit": "MWh", "value": 10})
        transaction = Transaction.from_xml(xml_data)
        self.assertEqual("MWh", transaction.unit())
        self.assertEqual(10, transaction.quantity())

    def test_computes_missing_quantity_data(self):
        biofuel = Biocarburant(name="EMAG")
        self.patched_MaterialConverter.return_value.from_udb_biofuel_code.return_value = biofuel
        self.patched_compute_lot_quantity.return_value = {"weight": 10, "volume": 20, "lhv_amount": 3600 * 10}

        xml_data = transaction_data(quantity={"unit": "MWh", "value": 10})
        transaction = Transaction.from_xml(xml_data)
        self.patched_compute_lot_quantity.assert_not_called()

        lot_attributes = transaction.to_lot_attributes()
        self.patched_compute_lot_quantity.assert_called_with(biofuel, {"lhv_amount": 3600 * 10})
        self.assertEqual(3600 * 10, lot_attributes["lhv_amount"])
        self.assertEqual(10, lot_attributes["weight"])
        self.assertEqual(20, lot_attributes["volume"])

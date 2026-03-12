from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from edelivery.ebms.converters import UDBConversionError
from edelivery.ebms.request_responses import BaseRequestResponse, EOGetTransactionResponse
from edelivery.tests.ebms.fixtures.udb_xml_data import transaction_data


class BaseRequestResponseTest(TestCase):
    @staticmethod
    def payload(request_id):
        return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<udb:GetSourcingContactByIDResponse
  xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="{request_id}"/>
  <!-- … -->
</udb:GetSourcingContactByIDResponse>"""

    def test_extract_request_id(self):
        response = BaseRequestResponse(self.payload("12345"))
        self.assertEqual("12345", response.request_id())


class BaseEOGetTransactionResponseTest(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.patched_Biocarburant = patch("edelivery.ebms.request_responses.Biocarburant").start()
        self.patched_Biocarburant.objects.get.return_value = Biocarburant()

        self.patched_CarbureLot = patch("edelivery.ebms.request_responses.CarbureLot").start()
        self.patched_CarbureLot.objects.get.return_value = MagicMock()

        self.patched_Entity = patch("edelivery.ebms.request_responses.Entity").start()
        self.patched_Entity.objects.get.return_value = Entity()

        self.patched_MatierePremiere = patch("edelivery.ebms.request_responses.MatierePremiere").start()
        self.patched_MatierePremiere.objects.get.return_value = MatierePremiere()

        self.patched_Transaction = patch("edelivery.ebms.request_responses.Transaction").start()
        self.patched_Transaction.return_value.to_lot_attributes.return_value = {
            "biofuel_code": "",
            "carbure_supplier_id": 11111,
            "feedstock_code": "",
            "lot_status": "",
        }

        self.patched_create_lot = patch("edelivery.ebms.request_responses.create_lot").start()
        self.patched_do_update_lot = patch("edelivery.ebms.request_responses.do_update_lot").start()
        self.patched_log_error = patch("edelivery.ebms.request_responses.log_error").start()

    def tearDown(self):
        patch.stopall()

    def payload(self, nb_transactions=1, **kwargs):
        transactions = "".join([transaction_data(**kwargs) for i in range(0, nb_transactions)])

        return f"""\
<udb:EOGetTransactionResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="e0907dde-11f5-423b-90e7-6a79728a5ef8"
            PROCESSING_DATE="2025-12-23T11:11:57.548+01:00"
            STATUS="FOUND" />
  <EO_TRANS_HEADER>
    {transactions}
  </EO_TRANS_HEADER>
</udb:EOGetTransactionResponse>"""


class EOGetTransactionResponseLeadingToLotCreationTest(BaseEOGetTransactionResponseTest):
    def setUp(self):
        super().setUp()

        self.patched_created_lot = MagicMock()
        self.patched_CarbureLot.objects.get.side_effect = [CarbureLot.DoesNotExist(), self.patched_created_lot]

    def test_fetches_supplier_entity(self):
        get_entity = self.patched_Entity.objects.get
        self.patched_Transaction.return_value.to_lot_attributes.return_value = {"carbure_supplier_id": 99999}
        response = EOGetTransactionResponse(self.payload())
        get_entity.assert_not_called()

        response.post_retrieval_action_result()
        get_entity.assert_called_with(id=99999)

    def test_creates_lot_if_not_already_existing(self):
        supplier = Entity()
        get_entity = self.patched_Entity.objects.get
        get_entity.return_value = supplier
        response = EOGetTransactionResponse(self.payload())
        self.patched_create_lot.assert_not_called()

        response.post_retrieval_action_result()
        self.patched_create_lot.assert_called_with(None, supplier, "UDB", ANY)

    def test_update_lot_status_as_a_separate_step(self):
        patched_carbure_status = self.patched_Transaction.return_value.carbure_status
        patched_carbure_status.return_value = "PENDING"
        response = EOGetTransactionResponse(self.payload())
        patched_carbure_status.assert_not_called()
        self.patched_created_lot.save.assert_not_called()

        response.post_retrieval_action_result()
        patched_carbure_status.assert_called()
        self.assertEqual("PENDING", self.patched_created_lot.lot_status)
        self.patched_created_lot.save.assert_called()

    def test_returns_created_lot_summary(self):
        self.patched_created_lot.id = 12345
        response = EOGetTransactionResponse(self.payload())
        result = response.post_retrieval_action_result()
        self.assertEqual([{"newLotCreated": True, "id": 12345}], result)


class EOGetTransactionResponseLeadingToLotUpdateTest(BaseEOGetTransactionResponseTest):
    def setUp(self):
        super().setUp()

        self.patched_existing_lot = MagicMock()
        self.patched_CarbureLot.objects.get.return_value = self.patched_existing_lot

    def test_updates_existing_lot(self):
        supplier = Entity()
        self.patched_existing_lot.carbure_supplier = supplier
        response = EOGetTransactionResponse(self.payload())
        self.patched_do_update_lot.assert_not_called()

        response.post_retrieval_action_result()
        self.patched_do_update_lot.assert_called_with(None, supplier, self.patched_existing_lot, ANY)

    def test_converts_biofuel_code_into_biofuel_id_before_calling_update_method(self):
        self.patched_Transaction.return_value.to_lot_attributes.return_value["biofuel_code"] = "B_CODE"
        patched_get = self.patched_Biocarburant.objects.get
        patched_get.return_value = Biocarburant(id=111)
        response = EOGetTransactionResponse(self.payload())
        patched_get.assert_not_called()

        response.post_retrieval_action_result()
        patched_get.assert_called_with(code="B_CODE")
        passed_attributes = self.patched_do_update_lot.call_args.args[3]
        self.assertNotIn("biofuel_code", passed_attributes)
        self.assertIn("biofuel_id", passed_attributes)
        self.assertEqual(111, passed_attributes["biofuel_id"])

    def test_converts_feedstock_code_into_feedstock_id_before_calling_update_method(self):
        self.patched_Transaction.return_value.to_lot_attributes.return_value["feedstock_code"] = "F_CODE"
        patched_get = self.patched_MatierePremiere.objects.get
        patched_get.return_value = MatierePremiere(id=111)
        response = EOGetTransactionResponse(self.payload())
        patched_get.assert_not_called()

        response.post_retrieval_action_result()
        patched_get.assert_called_with(code="F_CODE")
        passed_attributes = self.patched_do_update_lot.call_args.args[3]
        self.assertNotIn("feedstock_code", passed_attributes)
        self.assertIn("feedstock_id", passed_attributes)
        self.assertEqual(111, passed_attributes["feedstock_id"])

    def test_update_lot_status_as_a_separate_step(self):
        self.patched_existing_lot.lot_status = "SHOULD_CHANGE"
        patched_carbure_status = self.patched_Transaction.return_value.carbure_status
        patched_carbure_status.return_value = "PENDING"
        response = EOGetTransactionResponse(self.payload())
        self.assertEqual("SHOULD_CHANGE", self.patched_existing_lot.lot_status)
        patched_carbure_status.assert_not_called()
        self.patched_existing_lot.save.assert_not_called()

        response.post_retrieval_action_result()
        passed_attributes = self.patched_do_update_lot.call_args.args[3]
        patched_carbure_status.assert_called()
        self.assertNotIn("lot_status", passed_attributes)
        self.assertEqual("PENDING", self.patched_existing_lot.lot_status)
        self.patched_existing_lot.save.assert_called()

    def test_returns_updated_lot_summary(self):
        self.patched_existing_lot.id = 12345
        response = EOGetTransactionResponse(self.payload())
        result = response.post_retrieval_action_result()
        self.assertEqual([{"newLotCreated": False, "id": 12345}], result)


class EOGetTransactionResponseTest(BaseEOGetTransactionResponseTest):
    def test_looks_for_existing_carbure_lot_with_imported_udb_transaction_id(self):
        patched_get = self.patched_CarbureLot.objects.get
        self.patched_Transaction.return_value.udb_transaction_id.return_value = "111"

        response = EOGetTransactionResponse(self.payload())
        patched_get.assert_not_called()

        response.post_retrieval_action_result()
        patched_get.assert_called_with(udb_transaction_id="111")

    def test_converts_each_transactions_received(self):
        supplier = Entity(id=99999)
        self.patched_Entity.objects.get.return_value = supplier
        existing_lot = MagicMock(id="12345", carbure_supplier=supplier)
        created_lot = MagicMock(id="98765")
        self.patched_CarbureLot.objects.get.side_effect = [existing_lot, CarbureLot.DoesNotExist(), created_lot]
        self.patched_Transaction.return_value.to_lot_attributes.return_value["carbure_supplier_id"] = 99999

        response = EOGetTransactionResponse(self.payload(nb_transactions=2))
        result = response.post_retrieval_action_result()
        self.assertEqual([{"newLotCreated": False, "id": "12345"}, {"newLotCreated": True, "id": "98765"}], result)

    def test_logs_error_on_conversion_error(self):
        self.patched_Transaction.return_value.to_lot_attributes.side_effect = UDBConversionError("Oups")
        response = EOGetTransactionResponse(self.payload())
        self.patched_log_error.assert_not_called()

        result = response.post_retrieval_action_result()
        self.patched_log_error.assert_called_with("Unable to convert UDB transaction into CarbuRe lot", {"cause": "Oups"})
        self.assertEqual([{"error": "Unable to convert UDB transaction into CarbuRe lot", "cause": "Oups"}], result)

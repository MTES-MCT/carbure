from unittest import TestCase
from unittest.mock import ANY, patch

from core.models import CarbureLot
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


class EOGetTransactionResponseTest(TestCase):
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

    def setUp(self):
        self.patched_CarbureLot = patch("edelivery.ebms.request_responses.CarbureLot").start()
        self.patched_CarbureLot.objects.update_or_create.return_value = (CarbureLot(), True)

        self.patched_Transaction = patch("edelivery.ebms.request_responses.Transaction").start()
        self.patched_Transaction.return_value.to_lot_attributes.return_value = {}

        self.patched_log_error = patch("edelivery.ebms.request_responses.log_error").start()

    def tearDown(self):
        patch.stopall()

    def test_creates_or_updates_lot_after_response_retrieval(self):
        self.patched_Transaction.return_value.udb_transaction_id.return_value = "111"
        patched_update_or_create = self.patched_CarbureLot.objects.update_or_create
        patched_update_or_create.return_value = (CarbureLot(id="12345"), True)
        response = EOGetTransactionResponse(self.payload())
        patched_update_or_create.assert_not_called()

        result = response.post_retrieval_action_result()
        patched_update_or_create.assert_called_with(udb_transaction_id="111", defaults=ANY)
        self.assertEqual([{"newLotCreated": True, "id": "12345"}], result)

    def test_converts_each_transactions_received(self):
        patched_update_or_create = self.patched_CarbureLot.objects.update_or_create
        patched_update_or_create.side_effect = [(CarbureLot(id="111"), True), (CarbureLot(id="222"), False)]

        response = EOGetTransactionResponse(self.payload(nb_transactions=2))
        patched_update_or_create.assert_not_called()

        result = response.post_retrieval_action_result()
        self.assertEqual(2, patched_update_or_create.call_count)
        self.assertEqual([{"newLotCreated": True, "id": "111"}, {"newLotCreated": False, "id": "222"}], result)

    def test_logs_error_on_conversion_error(self):
        self.patched_Transaction.return_value.to_lot_attributes.side_effect = UDBConversionError("Oups")
        response = EOGetTransactionResponse(self.payload())
        self.patched_log_error.assert_not_called()

        result = response.post_retrieval_action_result()
        self.patched_log_error.assert_called_with("Unable to convert UDB transaction into CarbuRe lot", {"cause": "Oups"})
        self.assertEqual([{"error": "Unable to convert UDB transaction into CarbuRe lot", "cause": "Oups"}], result)

from datetime import datetime
from unittest.mock import patch

from edelivery.ebms.request_responses.eo_get_transaction_response import EOGetTransactionResponse
from edelivery.ebms.requests.eo_get_transaction_request import EOGetTransactionRequest

from .test_base_request import BaseRequestTest


@patch.dict("os.environ", {"CARBURE_NTR": "123"})
class EOGetTransactionRequestTest(BaseRequestTest):
    def test_knows_its_response_class(self):
        request = EOGetTransactionRequest("99999")
        self.assertEqual(EOGetTransactionResponse, request.response_class)

    def test_injects_transaction_id_in_body(self):
        request = EOGetTransactionRequest("99999")
        expected_body = """\
<udb:EOGetTransactionRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_GET_TRANS_HEADER>
    <EO_TRANSACTION>
      <TRANSACTION_ID>99999</TRANSACTION_ID>
    </EO_TRANSACTION>
  </EO_GET_TRANS_HEADER>
</udb:EOGetTransactionRequest>"""

        self.assertEqual(expected_body, request.body)

    def test_injects_several_transaction_ids_at_once(self):
        request = EOGetTransactionRequest("111", "222")
        expected_body = """\
<udb:EOGetTransactionRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_GET_TRANS_HEADER>
    <EO_TRANSACTION>
      <TRANSACTION_ID>111</TRANSACTION_ID>
      <TRANSACTION_ID>222</TRANSACTION_ID>
    </EO_TRANSACTION>
  </EO_GET_TRANS_HEADER>
</udb:EOGetTransactionRequest>"""

        self.assertEqual(expected_body, request.body)

    def test_injects_creation_date_range_in_body(self):
        d1 = datetime(2026, 1, 25, 8, 0)
        d2 = datetime(2026, 1, 25, 10, 0)
        request = EOGetTransactionRequest(from_creation_date=d1, to_creation_date=d2)
        expected_body = """\
<udb:EOGetTransactionRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_GET_TRANS_HEADER>
    <EO_ID_DETAIL_BY_CREATION_DATE>
      <ECONOMIC_OPERATOR_ID>123</ECONOMIC_OPERATOR_ID>
      <CREATION_DATE_FROM>2026-01-25T08:00:00+01:00</CREATION_DATE_FROM>
      <CREATION_DATE_TO>2026-01-25T10:00:00+01:00</CREATION_DATE_TO>
    </EO_ID_DETAIL_BY_CREATION_DATE>
  </EO_GET_TRANS_HEADER>
</udb:EOGetTransactionRequest>"""

        self.assertEqual(expected_body, request.body)

    @patch("edelivery.ebms.requests.eo_get_transaction_request.datetime")
    def test_defaults_to_creation_date_kwarg_to_now_if_from_creation_date_present(self, patched_datetime):
        patched_datetime.now.return_value = datetime(2026, 1, 25, 10, 0)
        request = EOGetTransactionRequest(from_creation_date=datetime(2026, 1, 25, 8, 0))

        expected_body = """\
<udb:EOGetTransactionRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_GET_TRANS_HEADER>
    <EO_ID_DETAIL_BY_CREATION_DATE>
      <ECONOMIC_OPERATOR_ID>123</ECONOMIC_OPERATOR_ID>
      <CREATION_DATE_FROM>2026-01-25T08:00:00+01:00</CREATION_DATE_FROM>
      <CREATION_DATE_TO>2026-01-25T10:00:00+01:00</CREATION_DATE_TO>
    </EO_ID_DETAIL_BY_CREATION_DATE>
  </EO_GET_TRANS_HEADER>
</udb:EOGetTransactionRequest>"""

        self.assertEqual(expected_body, request.body)

    def test_raises_an_error_if_range_incomplete(self):
        with self.assertRaises(ValueError) as context:
            EOGetTransactionRequest(to_creation_date=datetime(2026, 1, 25, 10, 0))

        self.assertEqual(
            "`from_creation_date` keyword argument can't be `None` when `to_creation_date` is set",
            str(context.exception),
        )

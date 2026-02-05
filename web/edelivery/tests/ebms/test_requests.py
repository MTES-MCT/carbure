from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.request_responses import BaseRequestResponse, EOGetTransactionResponse
from edelivery.ebms.requests import BaseRequest, EOGetTransactionRequest, GetSourcingContactByIdRequest


class BaseRequestTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.requests.new_uuid").start()

    def tearDown(self):
        patch.stopall()

    def test_inserts_request_id(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"
        request = BaseRequest("<request/>")
        expected_body = """\
<request>
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
</request>"""
        self.assertEqual(request.body, expected_body)

    @patch("edelivery.ebms.requests.zip_and_stream_udb_request")
    def test_zips_and_encodes_its_body(self, patched_zip_and_stream_udb_request):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"
        patched_zip_and_stream_udb_request.return_value = "abcdef"
        request = BaseRequest("<request/>")

        encoded_request = request.zipped_encoded()
        expected_body = """\
<request>
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
</request>"""
        patched_zip_and_stream_udb_request.assert_called_with(expected_body)
        self.assertEqual("abcdef", encoded_request)

    def test_knows_its_response_class(self):
        request = BaseRequest("<request/>")
        self.assertEqual(BaseRequestResponse, request.response_class)


class GetSourcingContactByIdRequestTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.requests.new_uuid").start()

    def tearDown(self):
        patch.stopall()

    def test_knows_its_identifier(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

        request = GetSourcingContactByIdRequest("")
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", request.id)

    def test_injects_request_id_and_sourcing_contact_id_in_body(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

        request = GetSourcingContactByIdRequest("99999")
        expected_body = """\
<udb:GetSourcingContactByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <SC_ID_HEADER>
    <SC_ID>
      <SOURCING_CONTACT_NUMBER>99999</SOURCING_CONTACT_NUMBER>
    </SC_ID>
  </SC_ID_HEADER>
</udb:GetSourcingContactByIDRequest>"""

        self.assertEqual(expected_body, request.body)


@patch.dict("os.environ", {"CARBURE_NTR": "123"})
class EOGetTransactionRequestTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.requests.new_uuid").start()
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

    def tearDown(self):
        patch.stopall()

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

    def test_raises_an_error_if_range_incomplete(self):
        with self.assertRaises(ValueError) as context:
            EOGetTransactionRequest(to_creation_date=datetime(2026, 1, 25, 10, 0))

        self.assertEqual(
            "`from_creation_date` keyword argument can't be `None` when `to_creation_date` is set",
            str(context.exception),
        )

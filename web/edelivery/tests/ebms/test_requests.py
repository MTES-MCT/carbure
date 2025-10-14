from unittest import TestCase
from unittest.mock import patch

from edelivery.ebms.requests import BaseRequest, GetSourcingContactByIdRequest


class BaseRequestTest(TestCase):
    @patch("edelivery.ebms.requests.zip_and_stream_udb_request")
    def test_zips_and_encodes_its_body(self, patched_zip_and_stream_udb_request):
        patched_zip_and_stream_udb_request.return_value = "abcdef"
        request = BaseRequest("12345", "<request/>")

        encoded_request = request.zipped_encoded()
        patched_zip_and_stream_udb_request.assert_called_with("<request/>")
        self.assertEqual("abcdef", encoded_request)


class GetSourcingContactByIdRequestTest(TestCase):
    def setUp(self):
        self.patched_new_uuid = patch("edelivery.ebms.requests.new_uuid").start()

    def test_knows_its_identifier(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

        request = GetSourcingContactByIdRequest("")
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", request.id)

    def test_injects_request_id_and_sourcing_contact_id_in_body(self):
        self.patched_new_uuid.return_value = "12345678-1234-1234-1234-1234567890ab"

        request = GetSourcingContactByIdRequest("99999")
        expected_body = """\
<udb:GetSourcingContactByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab"/>
  <SC_ID_HEADER>
    <SC_ID>
      <SOURCING_CONTACT_NUMBER>99999</SOURCING_CONTACT_NUMBER>
    </SC_ID>
  </SC_ID_HEADER>
</udb:GetSourcingContactByIDRequest>"""

        self.assertEqual(expected_body, request.body)

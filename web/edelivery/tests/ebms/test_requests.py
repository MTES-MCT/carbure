from edelivery.ebms.request_responses.get_certificate_response import GetCertificateResponse
from edelivery.ebms.requests_temp import (
    GetCertificateRequest,
    GetSourcingContactByIdRequest,
)

from .requests.test_base_request import BaseRequestTest


class GetCertificateRequestTest(BaseRequestTest):
    def test_knows_its_body(self):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

        request = GetCertificateRequest()
        expected_body = """\
<udb:GetCertificateRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
</udb:GetCertificateRequest>"""

        self.assertEqual(expected_body, request.body)

    def test_associates_to_GetCertificateResponse_class(self):
        request = GetCertificateRequest()
        self.assertIs(GetCertificateResponse, request.response_class)


class GetSourcingContactByIdRequestTest(BaseRequestTest):
    def test_knows_its_identifier(self):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

        request = GetSourcingContactByIdRequest("")
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", request.id)

    def test_injects_request_id_and_sourcing_contact_id_in_body(self):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

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

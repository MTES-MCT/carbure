from edelivery.ebms.request_responses.get_certificate_response import GetCertificateResponse
from edelivery.ebms.requests.get_certificate_request import GetCertificateRequest

from .test_base_request import BaseRequestTest


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

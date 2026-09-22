from edelivery.ebms.request_responses.get_organisation_by_id_response import GetOrganisationByIDResponse
from edelivery.ebms.requests.get_organisation_by_id_request import GetOrganisationByIDRequest

from .test_base_request import BaseRequestTest


class GetOrganisationByIDRequestTest(BaseRequestTest):
    def test_knows_its_body(self):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

        request = GetOrganisationByIDRequest("FR_SIREN_CD000001789")
        expected_body = """\
<udb:GetOrganisationByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_ID_HEADER>
    <EO_ID>
      <ECONOMIC_OPERATOR_NUMBER>FR_SIREN_CD000001789</ECONOMIC_OPERATOR_NUMBER>
    </EO_ID>
  </EO_ID_HEADER>
</udb:GetOrganisationByIDRequest>"""

        self.assertEqual(expected_body, request.body)

    def test_handles_several_entities(self):
        request = GetOrganisationByIDRequest("FR_SIREN_CD000001111", "FR_SIREN_CD000009999")
        expected_body = """\
<udb:GetOrganisationByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_ID_HEADER>
    <EO_ID>
      <ECONOMIC_OPERATOR_NUMBER>FR_SIREN_CD000001111</ECONOMIC_OPERATOR_NUMBER>
      <ECONOMIC_OPERATOR_NUMBER>FR_SIREN_CD000009999</ECONOMIC_OPERATOR_NUMBER>
    </EO_ID>
  </EO_ID_HEADER>
</udb:GetOrganisationByIDRequest>"""

        self.assertEqual(expected_body, request.body)

    def test_uses_GetOrganisationByIDResponse_as_request_response(self):
        request = GetOrganisationByIDRequest("FR_SIREN_CD000001111", "FR_SIREN_CD000009999")
        self.assertIs(GetOrganisationByIDResponse, request.response_class)

from core.models.entity import Entity
from core.models.geography import Pays
from edelivery.ebms.requests.add_organisation_request import AddOrganisationRequest

from .test_base_request import BaseRequestTest


class AddOrganisationRequestTest(BaseRequestTest):
    def test_knows_its_body(self):
        self.assertEqual("12345678-1234-1234-1234-1234567890ab", self.patched_new_uuid())

        france = Pays(code_pays="FR")
        carbure_entity = Entity(name="Some entity", registration_id="123456789", registered_country=france)
        request = AddOrganisationRequest(carbure_entity)
        expected_body = """\
<udb:AddOrganisationRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="12345678-1234-1234-1234-1234567890ab" />
  <EO_DETAIL_HEADER>
    <EO_DETAIL>
      <ECONOMIC_OPERATOR_NUMBER>FR_SIREN_CD123456789</ECONOMIC_OPERATOR_NUMBER>
      <ORGANISATION_NAME>Some entity</ORGANISATION_NAME>
      <COUNTRY_CODE>FR</COUNTRY_CODE>
      <LEGAL_TYPE>LEGAL_ENTITY</LEGAL_TYPE>
    </EO_DETAIL>
  </EO_DETAIL_HEADER>
</udb:AddOrganisationRequest>"""

        self.assertEqual(expected_body, request.body)

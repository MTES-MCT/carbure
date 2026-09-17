from xml.etree import ElementTree as ET

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

    def test_exports_several_entities_at_once(self):
        france = Pays(code_pays="FR")
        e1 = Entity(name="Entity 1", registration_id="111111111", registered_country=france)
        e2 = Entity(name="Entity 2", registration_id="222222222", registered_country=france)
        request = AddOrganisationRequest(e1, e2)

        xml = ET.fromstring(request.body)
        eo_number_elements = xml.findall(".//ECONOMIC_OPERATOR_NUMBER")
        self.assertEqual(["FR_SIREN_CD111111111", "FR_SIREN_CD222222222"], [e.text for e in eo_number_elements])

    def test_must_export_at_least_one_entity(self):
        with self.assertRaises(ValueError) as context:
            AddOrganisationRequest()

        self.assertEqual("Request should export at least one entity", context.exception.args[0])

import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from edelivery.ebms.requests.add_update_certificate_request import AddUpdateCertificateRequest

from .test_base_request import BaseRequestTest


class AddUpdateCertificateRequestTest(BaseRequestTest):
    @staticmethod
    def add_update_certificate_request_payload(entity_certificate):
        request = AddUpdateCertificateRequest(entity_certificate)
        return ET.fromstring(request.body)

    def setUp(self):
        super().setUp()
        self.entity = MagicMock(**{"ntr_id.return_value": ""})
        self.certificate = MagicMock(certificate_id="")
        self.entity_certificate = MagicMock(entity=self.entity, certificate=self.certificate)

    def test_knowns_its_body(self):
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)

        expected_tag = "{http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1}AddUpdateCertificateRequest"
        self.assertEqual(expected_tag, root_xml_element.tag)

    def test_injects_entity_NTR_id(self):
        self.entity.ntr_id.return_value = "SOME_NTR_ID"

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        eo_number_tag = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/ECONOMIC_OPERATOR_NUMBER")
        self.assertEqual("SOME_NTR_ID", eo_number_tag.text)

    def test_injects_certificate_id(self):
        self.certificate.certificate_id = "SN_UN_2026_0123"

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        certificate_number_tag = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/CERTIFICATE_NUMBER")
        self.assertEqual("SN_UN_2026_0123", certificate_number_tag.text)

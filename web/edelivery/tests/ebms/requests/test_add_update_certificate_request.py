import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

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
        self.certificate = MagicMock(
            certificate_id="",
            certificate_type="SYSTEME_NATIONAL",
            status="EXPIRED",
            valid_from=datetime(2026, 1, 31),
        )
        self.entity_certificate = MagicMock(entity=self.entity, certificate=self.certificate)

        module_to_patch = "edelivery.ebms.requests.add_update_certificate_request"
        patched_CertificateStatusConverter = patch(f"{module_to_patch}.CertificateStatusConverter").start()
        self.patched_to_udb = patched_CertificateStatusConverter.return_value.to_udb
        self.patched_to_udb.return_value = ""

    def tearDown(self):
        patch.stopall()

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

    def test_injects_converted_status(self):
        self.certificate.status = "VALID"
        self.patched_to_udb.return_value = "UDB_STATUS"

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        self.patched_to_udb.assert_called_with("VALID")

        validity_status_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/VALIDITY_STATUS")
        self.assertEqual("UDB_STATUS", validity_status_element.text)

    def test_injects_issue_date(self):
        self.certificate.valid_from = datetime(2026, 6, 15, tzinfo=timezone.utc)
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)

        issue_date_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/DATE_OF_ISSUE")
        self.assertEqual("2026-06-15+00:00", issue_date_element.text)

    def test_sets_place_of_issue_to_France(self):
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        issue_location_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/PLACE_OF_ISSUE")
        self.assertEqual("France", issue_location_element.text)

    def test_raises_an_error_if_certificate_not_national_scheme(self):
        self.certificate.certificate_type = "ISCC"
        with self.assertRaises(NotImplementedError):
            AddUpdateCertificateRequest(self.entity_certificate)

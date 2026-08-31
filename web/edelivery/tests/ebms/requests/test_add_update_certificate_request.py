import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from edelivery.ebms.certificate_site import CertificateSite
from edelivery.ebms.requests.add_update_certificate_request import AddUpdateCertificateRequest

from .test_base_request import BaseRequestTest


class AddUpdateCertificateRequestTest(BaseRequestTest):
    @staticmethod
    def add_update_certificate_request_payload(entity_certificate):
        request = AddUpdateCertificateRequest(entity_certificate)
        return ET.fromstring(request.body)

    def setUp(self):
        super().setUp()
        self.entity = MagicMock(**{"ntr_id.return_value": "", "get_sites.return_value": []})
        self.certificate = MagicMock(
            certificate_id="",
            certificate_type="SYSTEME_NATIONAL",
            certificate_issuer="",
            scope="PB",
            status="EXPIRED",
            valid_from=datetime(2026, 1, 31),
            valid_until=datetime(2027, 2, 17),
        )
        self.entity_certificate = MagicMock(entity=self.entity, certificate=self.certificate)

        module_to_patch = "edelivery.ebms.requests.add_update_certificate_request"

        self.patched_CertificateIssuerConverter = patch(f"{module_to_patch}.CertificateIssuerConverter").start()
        self.patched_CertificateIssuerConverter.return_value.to_udb.return_value = ""

        self.patched_CertificateStatusConverter = patch(f"{module_to_patch}.CertificateStatusConverter").start()
        self.patched_CertificateStatusConverter.return_value.to_udb.return_value = ""

        self.patched_CertificateSite = patch(f"{module_to_patch}.CertificateSite").start()
        self.patched_CertificateSite.from_carbure_site.side_effect = lambda _: CertificateSite.from_xml("<SOME_TAG />")

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

    def test_injects_certificate_issuer(self):
        self.certificate.certificate_issuer = "SOME_ISSUER"
        patched_to_udb = self.patched_CertificateIssuerConverter.return_value.to_udb
        patched_to_udb.return_value = "SOME_CERTIFICATE_BODY_NUMBER"

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        patched_to_udb.assert_called_with("SOME_ISSUER")

        certificate_body_number_tag = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/CERTIFICATE_BODY_NUMBER")
        self.assertEqual("SOME_CERTIFICATE_BODY_NUMBER", certificate_body_number_tag.text)

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

    def test_sets_validity_start_date(self):
        self.certificate.valid_from = datetime(2026, 6, 15, tzinfo=timezone.utc)

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        validity_start_date_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/CERT_DATE_FROM")
        self.assertEqual("2026-06-15+00:00", validity_start_date_element.text)

    def test_sets_validity_end_date(self):
        self.certificate.valid_until = datetime(2026, 6, 17, tzinfo=timezone.utc)

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        validity_end_date_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/CERT_DATE_TO")
        self.assertEqual("2026-06-17+00:00", validity_end_date_element.text)

    def test_injects_converted_status(self):
        self.certificate.status = "VALID"
        patched_to_udb = self.patched_CertificateStatusConverter.return_value.to_udb
        patched_to_udb.return_value = "UDB_STATUS"

        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        patched_to_udb.assert_called_with("VALID")

        validity_status_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/VALIDITY_STATUS")
        self.assertEqual("UDB_STATUS", validity_status_element.text)

    def test_sets_group_certification_to_no(self):
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        group_certification_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/GROUP_CERTIFICATION")
        self.assertEqual("NO", group_certification_element.text)

    def test_sets_eo_scope(self):
        self.certificate.scope = "FSP"
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        scope = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/EO_SCOPE/ORGANISATION_SCOPE")
        self.assertEqual("FSP", scope.text)

    def test_handles_multiple_scopes(self):
        self.certificate.scope = "PB, FSP"
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        organisation_scopes = root_xml_element.findall("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/EO_SCOPE/ORGANISATION_SCOPE")
        self.assertEqual(["PB", "FSP"], [s.text for s in organisation_scopes])

    def test_injects_site_infos(self):
        patched_from_carbure_site = self.patched_CertificateSite.from_carbure_site
        patched_from_carbure_site.side_effect = [CertificateSite.from_xml("<SOME_TAG>Some value</SOME_TAG>")]

        carbure_site = MagicMock()
        self.entity.get_sites.return_value = [carbure_site]
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        patched_from_carbure_site.assert_called_with(carbure_site)

        site_element = root_xml_element.find("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/SOME_TAG")
        self.assertEqual("Some value", site_element.text)

    def test_handles_multiple_sites(self):
        patched_from_carbure_site = self.patched_CertificateSite.from_carbure_site
        patched_from_carbure_site.side_effect = [
            CertificateSite.from_xml("<SOME_TAG>Site 1</SOME_TAG>"),
            CertificateSite.from_xml("<SOME_TAG>Site 2</SOME_TAG>"),
        ]

        self.entity.get_sites.return_value = [MagicMock(), MagicMock()]
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)
        self.assertEqual(2, patched_from_carbure_site.call_count)

        sites = root_xml_element.findall("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/SOME_TAG")
        self.assertEqual(["Site 1", "Site 2"], [s.text for s in sites])

    def test_inserts_main_site_tag(self):
        self.entity.get_sites.return_value = [MagicMock(), MagicMock()]
        root_xml_element = self.add_update_certificate_request_payload(self.entity_certificate)

        main_sites = root_xml_element.findall("./EO_CERTIFICATE_HEADER/EO_CERTIFICATE/SOME_TAG/MAIN_SITE")
        self.assertEqual(["true", "false"], [ms.text for ms in main_sites])

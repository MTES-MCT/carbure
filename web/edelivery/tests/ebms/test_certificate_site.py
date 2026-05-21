from unittest import TestCase

from edelivery.ebms.certificate_site import CertificateSite
from edelivery.tests.ebms.fixtures.certificate_site_xml_data import certificate_site_xml_data


class CertificateSiteTest(TestCase):
    def check_carbure_attribute_corresponds_to_UDB_attribute(self, carbure_attribute, udb_attribute, value):
        xml_data = certificate_site_xml_data(**{udb_attribute: value})
        site = CertificateSite.from_xml(xml_data)
        site_value = getattr(site, udb_attribute)()
        self.assertEqual(value, site_value)

        site_attributes = site.to_site_attributes()
        self.assertEqual(value, site_attributes[carbure_attribute])

    def test_knows_its_name(self):
        self.check_carbure_attribute_corresponds_to_UDB_attribute("name", "name", "A Site")

    def test_knows_its_address(self):
        self.check_carbure_attribute_corresponds_to_UDB_attribute("address", "street_line", "221, Baker Street")

    def test_knows_its_zipcode(self):
        self.check_carbure_attribute_corresponds_to_UDB_attribute("postal_code", "zipcode", "69100")

    def test_knows_its_city(self):
        self.check_carbure_attribute_corresponds_to_UDB_attribute("city", "city", "Villeurbanne")

    def test_knows_its_country(self):
        self.check_carbure_attribute_corresponds_to_UDB_attribute("country_code", "country_code", "BE")

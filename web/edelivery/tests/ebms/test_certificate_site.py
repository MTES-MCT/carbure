from unittest import TestCase

from core.models.geography import Pays
from edelivery.ebms.certificate_site import CertificateSite
from edelivery.tests.ebms.fixtures.certificate_site_xml_data import certificate_site_xml_data
from transactions.models.site import Site


class CertificateSiteTest(TestCase):
    def check_carbure_attribute_corresponds_to_UDB_attribute(self, carbure_attribute, udb_attribute, value):
        xml_data = certificate_site_xml_data(**{udb_attribute: value})
        site = CertificateSite.from_xml(xml_data)
        site_value = getattr(site, udb_attribute)()
        self.assertEqual(value, site_value)

        site_attributes = site.to_site_attributes()
        self.assertEqual(value, site_attributes[carbure_attribute])

    def check_UDB_attribute_corresponds_to_carbure_attribute(self, carbure_attribute, udb_attribute, value):
        carbure_site = Site(**{carbure_attribute: value})
        site = CertificateSite.from_carbure_site(carbure_site)
        site_value = getattr(site, udb_attribute)()
        self.assertEqual(value, site_value)

    def check_attributes_correspondance(self, carbure_attribute, udb_attribute):
        self.check_carbure_attribute_corresponds_to_UDB_attribute(carbure_attribute, udb_attribute, value="Some value")
        self.check_UDB_attribute_corresponds_to_carbure_attribute(carbure_attribute, udb_attribute, value="Some value")

    def test_knows_its_name(self):
        self.check_attributes_correspondance("name", "name")

    def test_knows_its_address(self):
        self.check_attributes_correspondance("address", "street_line")

    def test_knows_its_zipcode(self):
        self.check_attributes_correspondance("postal_code", "zipcode")

    def test_knows_its_city(self):
        self.check_attributes_correspondance("city", "city")

    def test_knows_its_country_code(self):
        xml_data = certificate_site_xml_data(country_code="BE")
        site = CertificateSite.from_xml(xml_data)
        country_code = site.country_code()
        self.assertEqual("BE", country_code)

    def test_knows_country_code_from_carbure_site(self):
        country = Pays(code_pays="BE")
        carbure_site = Site(country=country)
        site = CertificateSite.from_carbure_site(carbure_site)
        country_code = site.country_code()
        self.assertEqual("BE", country_code)

from unittest import TestCase

from core.models.geography import Pays
from edelivery.ebms.certificate_site import CertificateSite
from entity.factories.entity import EntityFactory
from transactions.models.site import Site


class CertificateSiteTest(TestCase):
    def test_builds_from_carbure_site(self):
        country = Pays(code_pays="BE")
        carbure_site = Site(
            name="Site name",
            address="Some address",
            postal_code="Some zipcode",
            city="Some city",
            country=country,
        )
        site = CertificateSite.from_carbure_site(carbure_site)
        self.assertEqual("Site name", site.name())
        self.assertEqual("Some address", site.street_line())
        self.assertEqual("Some zipcode", site.zipcode())
        self.assertEqual("Some city", site.city())
        self.assertEqual("BE", site.country_code())

    def test_is_not_main_site_when_created_from_carbure_site(self):
        country = Pays(code_pays="BE")
        carbure_site = Site(country=country)
        site = CertificateSite.from_carbure_site(carbure_site)
        is_main_site = site.xml_root_element.find("./MAIN_SITE")
        self.assertEqual("false", is_main_site.text)
        self.assertFalse(site.is_main_site())

    def test_builds_from_carbure_entity(self):
        country = Pays(code_pays="BE")
        carbure_entity = EntityFactory.build(
            name="Site name",
            registered_address="Some address",
            registered_zipcode="Some zipcode",
            registered_city="Some city",
            registered_country=country,
        )
        site = CertificateSite.from_carbure_entity(carbure_entity)
        self.assertEqual("Site name", site.name())
        self.assertEqual("Some address", site.street_line())
        self.assertEqual("Some zipcode", site.zipcode())
        self.assertEqual("Some city", site.city())
        self.assertEqual("BE", site.country_code())

    def test_is_main_site_when_created_from_carbure_entity(self):
        carbure_entity = EntityFactory.build()
        site = CertificateSite.from_carbure_entity(carbure_entity)
        is_main_site = site.xml_root_element.find("./MAIN_SITE")
        self.assertEqual("true", is_main_site.text)
        self.assertTrue(site.is_main_site())

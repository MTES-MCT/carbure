from unittest import TestCase

from edelivery.ebms.certificate import Certificate
from edelivery.tests.ebms.fixtures.certificate_xml_data import certificate_xml_data


class CertificateTest(TestCase):
    def test_fetches_sites(self):
        xml_data = certificate_xml_data(
            sites=[
                {"name": "Site1", "zipcode": "75020", "city": "Paris"},
                {"name": "Site2", "zipcode": "69100", "city": "Villeurbanne"},
                {"name": "Site2", "zipcode": "75020", "city": "Paris 20"},
            ],
        )
        certificate = Certificate.from_xml(xml_data)
        sites = certificate.sites()
        self.assertEqual(3, len(sites))
        self.assertEqual("Site1", sites[0].name())
        self.assertEqual("69100", sites[1].zipcode())
        self.assertEqual("Paris 20", sites[2].city())

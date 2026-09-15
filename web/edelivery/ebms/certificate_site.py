from edelivery.ebms.udb_element import UDBElement


class CertificateSite(UDBElement):
    @staticmethod
    def from_carbure_site(carbure_site):
        country_code = carbure_site.country and carbure_site.country.code_pays

        return CertificateSite.from_xml(f"""\
<EO_CERTIFICATE_SITE>
    <SITE_NAME>{carbure_site.name}</SITE_NAME>
    <STREET_LINE>{carbure_site.address}</STREET_LINE>
    <POST_CODE>{carbure_site.postal_code}</POST_CODE>
    <CITY>{carbure_site.city}</CITY>
    <COUNTRY_CODE>{country_code}</COUNTRY_CODE>
</EO_CERTIFICATE_SITE>
        """)

    def city(self):
        return self.xml_root_element.find("./CITY").text

    def country_code(self):
        return self.xml_root_element.find("./COUNTRY_CODE").text

    def name(self):
        return self.xml_root_element.find("./SITE_NAME").text

    def street_line(self):
        return self.xml_root_element.find("./STREET_LINE").text

    def zipcode(self):
        return self.xml_root_element.find("./POST_CODE").text

    def to_site_attributes(self):
        return {
            "address": self.street_line(),
            "city": self.city(),
            "name": self.name(),
            "postal_code": self.zipcode(),
        }

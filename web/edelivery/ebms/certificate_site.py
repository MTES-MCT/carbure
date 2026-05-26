from edelivery.ebms.udb_element import UDBElement


class CertificateSite(UDBElement):
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
            "country_code": self.country_code(),
            "name": self.name(),
            "postal_code": self.zipcode(),
        }

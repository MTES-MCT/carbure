from edelivery.ebms.udb_element import UDBElement


class CertificateSite(UDBElement):
    @staticmethod
    def from_carbure_entity(carbure_entity):
        country_code = carbure_entity.registered_country and carbure_entity.registered_country.code_pays

        return CertificateSite.from_raw_data(
            name=carbure_entity.name,
            address=carbure_entity.registered_address,
            zipcode=carbure_entity.registered_zipcode,
            city=carbure_entity.registered_city,
            country_code=country_code,
            is_main_site=True,
        )

    @staticmethod
    def from_carbure_site(carbure_site):
        country_code = carbure_site.country and carbure_site.country.code_pays

        return CertificateSite.from_raw_data(
            name=carbure_site.name,
            address=carbure_site.address,
            zipcode=carbure_site.postal_code,
            city=carbure_site.city,
            country_code=country_code,
            is_main_site=False,
        )

    @staticmethod
    def from_raw_data(name, address, zipcode, city, country_code, is_main_site):
        if not address:
            raise ValueError("Param `address` should not be empty")

        if not zipcode:
            raise ValueError("Param `zipcode` should not be empty")

        if not city:
            raise ValueError("Param `city` should not be empty")

        if not country_code:
            raise ValueError("Param `country_code` should not be empty")

        return CertificateSite.from_xml(f"""\
<EO_CERTIFICATE_SITE>
    <SITE_NAME>{name}</SITE_NAME>
    <STREET_LINE>{address}</STREET_LINE>
    <POST_CODE>{zipcode}</POST_CODE>
    <CITY>{city}</CITY>
    <COUNTRY_CODE>{country_code}</COUNTRY_CODE>
    <MAIN_SITE>{str(is_main_site).lower()}</MAIN_SITE>
</EO_CERTIFICATE_SITE>
        """)

    def city(self):
        return self.xml_root_element.find("./CITY").text

    def country_code(self):
        return self.xml_root_element.find("./COUNTRY_CODE").text

    def is_main_site(self):
        return self.xml_root_element.find("./MAIN_SITE").text == "true"

    def name(self):
        return self.xml_root_element.find("./SITE_NAME").text

    def street_line(self):
        return self.xml_root_element.find("./STREET_LINE").text

    def zipcode(self):
        return self.xml_root_element.find("./POST_CODE").text

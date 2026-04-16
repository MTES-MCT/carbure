from edelivery.ebms.certificate_site import CertificateSite
from edelivery.ebms.udb_element import UDBElement


class Certificate(UDBElement):
    def sites(self):
        return [CertificateSite(site_fragment) for site_fragment in self.xml_root_element.iter("EO_CERTIFICATE_SITE")]

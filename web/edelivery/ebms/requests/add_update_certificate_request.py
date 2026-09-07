import xml.etree.ElementTree as ET

from core.models.certificate import GenericCertificate
from edelivery.adapters.clock import to_date_isoformat
from edelivery.ebms.certificate_site import CertificateSite
from edelivery.ebms.converters import CertificateIssuerConverter, CertificateStatusConverter

from .base_request import BaseRequest


class AddUpdateCertificateRequest(BaseRequest):
    @staticmethod
    def eo_scope_xml_elements(scopes):
        return "\n".join([f"<EO_SCOPE><ORGANISATION_SCOPE>{s}</ORGANISATION_SCOPE></EO_SCOPE>" for s in scopes])

    @staticmethod
    def site_xml_elements(sites):
        for i, s in enumerate(sites):
            main_site_element = ET.Element("MAIN_SITE")
            main_site_element.text = "true" if (i == 0) else "false"
            s.xml_root_element.append(main_site_element)

        return "\n".join([f"{s.to_xml()}" for s in sites])

    def __init__(self, entity_certificate):
        certificate = entity_certificate.certificate
        certificate_type = certificate.certificate_type
        if certificate_type != GenericCertificate.SYSTEME_NATIONAL:
            raise NotImplementedError(f"Certificate export to UDB not implemented for certificate type {certificate_type}")

        entity = entity_certificate.entity
        certificate_body_number = CertificateIssuerConverter().to_udb(certificate.certificate_issuer)
        validity_status = CertificateStatusConverter().to_udb(certificate.status)
        scopes = certificate.scope.split(", ")
        sites = [CertificateSite.from_carbure_site(s) for s in entity.get_sites()]
        payload = f"""\
<udb:AddUpdateCertificateRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_CERTIFICATE_HEADER>
    <EO_CERTIFICATE>
      <ECONOMIC_OPERATOR_NUMBER>{entity.ntr_id()}</ECONOMIC_OPERATOR_NUMBER>
      <CERTIFICATE_NUMBER>{certificate.certificate_id}</CERTIFICATE_NUMBER>
      <CERTIFICATE_BODY_NUMBER>{certificate_body_number}</CERTIFICATE_BODY_NUMBER>
      <DATE_OF_ISSUE>{to_date_isoformat(certificate.valid_from)}</DATE_OF_ISSUE>
      <PLACE_OF_ISSUE>France</PLACE_OF_ISSUE>
      <CERT_DATE_FROM>{to_date_isoformat(certificate.valid_from)}</CERT_DATE_FROM>
      <CERT_DATE_TO>{to_date_isoformat(certificate.valid_until)}</CERT_DATE_TO>
      <VALIDITY_STATUS>{validity_status}</VALIDITY_STATUS>
      <GROUP_CERTIFICATION>NO</GROUP_CERTIFICATION>
      {self.eo_scope_xml_elements(scopes)}
      {self.site_xml_elements(sites)}
      {self.stubbed_additional_mandatory_fields()}
    </EO_CERTIFICATE>
  </EO_CERTIFICATE_HEADER>
</udb:AddUpdateCertificateRequest>"""

        super().__init__(payload)

    def stubbed_additional_mandatory_fields(self):
        return """\
<CHAIN_OF_CUSTODIES>
  <CHAIN_OF_CUSTODY>Segregation</CHAIN_OF_CUSTODY>
</CHAIN_OF_CUSTODIES>
        """

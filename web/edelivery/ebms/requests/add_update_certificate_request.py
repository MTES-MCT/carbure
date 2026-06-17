from core.models.certificate import GenericCertificate
from edelivery.adapters.clock import to_date_isoformat
from edelivery.ebms.converters import CertificateStatusConverter

from .base_request import BaseRequest


class AddUpdateCertificateRequest(BaseRequest):
    def __init__(self, entity_certificate):
        certificate = entity_certificate.certificate
        certificate_type = certificate.certificate_type
        if certificate_type != GenericCertificate.SYSTEME_NATIONAL:
            raise NotImplementedError(f"Certificate export to UDB not implemented for certificate type {certificate_type}")

        entity = entity_certificate.entity
        validity_status = CertificateStatusConverter().to_udb(certificate.status)
        payload = f"""\
<udb:AddUpdateCertificateRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_CERTIFICATE_HEADER>
    <EO_CERTIFICATE>
      <ECONOMIC_OPERATOR_NUMBER>{entity.ntr_id()}</ECONOMIC_OPERATOR_NUMBER>
      <CERTIFICATE_NUMBER>{certificate.certificate_id}</CERTIFICATE_NUMBER>
      <VALIDITY_STATUS>{validity_status}</VALIDITY_STATUS>
      <DATE_OF_ISSUE>{to_date_isoformat(certificate.valid_from)}</DATE_OF_ISSUE>
      <PLACE_OF_ISSUE>France</PLACE_OF_ISSUE>
      <CERT_DATE_FROM>{to_date_isoformat(certificate.valid_from)}</CERT_DATE_FROM>
      <CERT_DATE_TO>{to_date_isoformat(certificate.valid_until)}</CERT_DATE_TO>
    </EO_CERTIFICATE>
  </EO_CERTIFICATE_HEADER>
</udb:AddUpdateCertificateRequest>"""

        super().__init__(payload)

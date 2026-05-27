from .base_request import BaseRequest


class AddUpdateCertificateRequest(BaseRequest):
    def __init__(self, entity_certificate):
        entity = entity_certificate.entity
        certificate = entity_certificate.certificate
        payload = f"""\
<udb:AddUpdateCertificateRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_CERTIFICATE_HEADER>
    <EO_CERTIFICATE>
      <ECONOMIC_OPERATOR_NUMBER>{entity.ntr_id()}</ECONOMIC_OPERATOR_NUMBER>
      <CERTIFICATE_NUMBER>{certificate.certificate_id}</CERTIFICATE_NUMBER>
    </EO_CERTIFICATE>
  </EO_CERTIFICATE_HEADER>
</udb:AddUpdateCertificateRequest>"""

        super().__init__(payload)

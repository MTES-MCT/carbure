from edelivery.ebms.request_responses.get_certificate_response import GetCertificateResponse
from edelivery.ebms.requests.base_request import BaseRequest


class GetCertificateRequest(BaseRequest):
    def __init__(self):
        body = """\
<udb:GetCertificateRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
</udb:GetCertificateRequest>"""
        super().__init__(body, GetCertificateResponse)


class GetSourcingContactByIdRequest(BaseRequest):
    def __init__(self, sourcing_contact_id):
        super().__init__(f"""\
<udb:GetSourcingContactByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <SC_ID_HEADER>
    <SC_ID>
      <SOURCING_CONTACT_NUMBER>{sourcing_contact_id}</SOURCING_CONTACT_NUMBER>
    </SC_ID>
  </SC_ID_HEADER>
</udb:GetSourcingContactByIDRequest>""")

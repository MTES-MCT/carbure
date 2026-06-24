from edelivery.ebms.request_responses.get_certificate_response import GetCertificateResponse

from .base_request import BaseRequest


class GetCertificateRequest(BaseRequest):
    def __init__(self):
        body = """\
<udb:GetCertificateRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
</udb:GetCertificateRequest>"""
        super().__init__(body, GetCertificateResponse)

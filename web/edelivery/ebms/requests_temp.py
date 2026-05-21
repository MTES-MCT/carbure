from datetime import datetime
from os import environ

from edelivery.ebms.request_responses.eo_get_transaction_response import EOGetTransactionResponse
from edelivery.ebms.request_responses.get_certificate_response import GetCertificateResponse
from edelivery.ebms.requests.base_request import BaseRequest


class EOGetTransactionRequest(BaseRequest):
    def __init__(self, *args, **kwargs):
        search_fragment = self.search_fragment(*args, **kwargs)
        body = f"""\
<udb:EOGetTransactionRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_GET_TRANS_HEADER>
    {search_fragment}
  </EO_GET_TRANS_HEADER>
</udb:EOGetTransactionRequest>"""

        super().__init__(body, EOGetTransactionResponse)

    def search_fragment(self, *args, **kwargs):
        if "to_creation_date" in kwargs and "from_creation_date" not in kwargs:
            raise ValueError("`from_creation_date` keyword argument can't be `None` when `to_creation_date` is set")

        if "from_creation_date" in kwargs:
            to_creation_date = kwargs["to_creation_date"] if "to_creation_date" in kwargs else datetime.now()

            return f"""\
<EO_ID_DETAIL_BY_CREATION_DATE>
  <ECONOMIC_OPERATOR_ID>{environ["CARBURE_NTR"]}</ECONOMIC_OPERATOR_ID>
  <CREATION_DATE_FROM>{kwargs["from_creation_date"].astimezone().isoformat()}</CREATION_DATE_FROM>
  <CREATION_DATE_TO>{to_creation_date.astimezone().isoformat()}</CREATION_DATE_TO>
</EO_ID_DETAIL_BY_CREATION_DATE>"""

        xml_fragment = "".join([f"<TRANSACTION_ID>{transaction_id}</TRANSACTION_ID>" for transaction_id in args])
        return f"""\
<EO_TRANSACTION>
  {xml_fragment}
</EO_TRANSACTION>"""


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

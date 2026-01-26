import xml.etree.ElementTree as ET

from edelivery.adapters.uuid_generator import new_uuid
from edelivery.adapters.zip_utils import zip_and_stream_udb_request
from edelivery.ebms.request_responses import BaseRequestResponse, EOGetTransactionResponse


class BaseRequest:
    @staticmethod
    def with_request_id_inserted(request_id, body):
        ET.register_namespace("udb", "http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1")
        xml = ET.fromstring(body)
        request_header_element = ET.Element("REQUEST_HEADER", {"REQUEST_ID": request_id})
        xml.insert(0, request_header_element)
        ET.indent(xml)
        return ET.tostring(xml, encoding="utf-8").decode("utf-8")

    def __init__(self, body, response_class=BaseRequestResponse):
        self.id = new_uuid()
        self.body = self.with_request_id_inserted(self.id, body)
        self.response_class = response_class

    def zipped_encoded(self):
        return zip_and_stream_udb_request(self.body)


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


class EOGetTransactionRequest(BaseRequest):
    def __init__(self, *args):
        xml_fragment = "".join([f"<TRANSACTION_ID>{transaction_id}</TRANSACTION_ID>" for transaction_id in args])
        body = f"""\
<udb:EOGetTransactionRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <EO_GET_TRANS_HEADER>
    <EO_TRANSACTION>
      {xml_fragment}
    </EO_TRANSACTION>
  </EO_GET_TRANS_HEADER>
</udb:EOGetTransactionRequest>"""

        super().__init__(body, EOGetTransactionResponse)

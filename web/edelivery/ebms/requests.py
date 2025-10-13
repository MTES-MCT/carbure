from os import environ

from edelivery.adapters.clock import timestamp
from edelivery.adapters.uuid_generator import new_uuid
from edelivery.adapters.zip_utils import zip_and_stream_udb_request
from edelivery.ebms.access_points import Responder


class BaseRequest:
    def __init__(self, responder_id, body):
        self.responder = Responder(responder_id)
        self.timestamp = timestamp()
        self.body = body

    def responder_to_XML(self):
        return self.responder.to_XML()

    def zipped_encoded(self):
        return zip_and_stream_udb_request(self.body)


class GetSourcingContactByIdRequest(BaseRequest):
    def __init__(self, responder_id, sourcing_contact_id):
        self.id = new_uuid()
        body = f"""\
<udb:GetSourcingContactByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="{self.id}"/>
  <SC_ID_HEADER>
    <SC_ID>
      <SOURCING_CONTACT_NUMBER>{sourcing_contact_id}</SOURCING_CONTACT_NUMBER>
    </SC_ID>
  </SC_ID_HEADER>
</udb:GetSourcingContactByIDRequest>"""
        super().__init__(responder_id, body)


class TestRequest(BaseRequest):
    def __init__(self):
        super().__init__(environ["INITIATOR_ACCESS_POINT_ID"], "<test>Hello World!</test>")

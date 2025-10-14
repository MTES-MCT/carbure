from edelivery.adapters.uuid_generator import new_uuid
from edelivery.adapters.zip_utils import zip_and_stream_udb_request


class BaseRequest:
    def __init__(self, request_id, body):
        self.id = request_id
        self.body = body

    def zipped_encoded(self):
        return zip_and_stream_udb_request(self.body)


class GetSourcingContactByIdRequest(BaseRequest):
    def __init__(self, sourcing_contact_id):
        request_id = new_uuid()
        body = f"""\
<udb:GetSourcingContactByIDRequest xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <REQUEST_HEADER REQUEST_ID="{request_id}"/>
  <SC_ID_HEADER>
    <SC_ID>
      <SOURCING_CONTACT_NUMBER>{sourcing_contact_id}</SOURCING_CONTACT_NUMBER>
    </SC_ID>
  </SC_ID_HEADER>
</udb:GetSourcingContactByIDRequest>"""
        super().__init__(request_id, body)
